import xml.etree.ElementTree as ET
import os
import math
from datetime import datetime
import argparse

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2.0)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def analyze_gpx(gpx_dir):
    workouts = []
    if not os.path.exists(gpx_dir):
        return []
    for filename in os.listdir(gpx_dir):
        if not filename.endswith('.gpx'): continue
        filepath = os.path.join(gpx_dir, filename)
        tree = ET.parse(filepath)
        root = tree.getroot()
        ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
        total_dist, total_ele_gain = 0.0, 0.0
        prev_lat, prev_lon, prev_ele = None, None, None
        
        pts = root.findall('.//gpx:trkpt', ns)
        if not pts:
             pts = root.findall('.//{http://www.topografix.com/GPX/1/1}trkpt')
             
        for pt in pts:
            lat, lon = float(pt.get('lat')), float(pt.get('lon'))
            ele_elem = pt.find('{http://www.topografix.com/GPX/1/1}ele')
            ele = float(ele_elem.text) if ele_elem is not None else 0.0
            
            if prev_lat is not None and prev_lon is not None:
                dist = haversine(prev_lat, prev_lon, lat, lon)
                total_dist += dist
                if ele > prev_ele:
                    total_ele_gain += (ele - prev_ele)
            prev_lat, prev_lon, prev_ele = lat, lon, ele

        if total_dist > 0:
            workouts.append({'dist_km': total_dist/1000.0, 'ele_gain': total_ele_gain})
    return workouts

def analyze_export(file_path, start_date=None):
    data = {
        'steps': {}, 'rhr': [], 'vo2max': [],
        'steadiness': [], 'burn': []
    }
    context = ET.iterparse(file_path, events=('end',))
    for event, elem in context:
        tag = elem.tag
        if tag == 'Record':
            rec_type = elem.get('type')
            val = elem.get('value')
            date_str = elem.get('startDate')
            if not date_str: continue
            rec_date = date_str[:10]
            
            if start_date and rec_date < start_date:
                elem.clear()
                continue
                
            if rec_type == 'HKQuantityTypeIdentifierStepCount' and val:
                data['steps'][rec_date] = data['steps'].get(rec_date, 0) + float(val)
            elif rec_type == 'HKQuantityTypeIdentifierRestingHeartRate' and val:
                data['rhr'].append(float(val))
            elif rec_type == 'HKQuantityTypeIdentifierVO2Max' and val:
                data['vo2max'].append(float(val))
            elif rec_type == 'HKQuantityTypeIdentifierAppleWalkingSteadiness' and val:
                data['steadiness'].append(float(val))
                
        elif tag == 'ActivitySummary':
            move = elem.get('activeEnergyBurned')
            if move and float(move) > 0:
                data['burn'].append(float(move))
                
        elem.clear()
    return data

def main():
    parser = argparse.ArgumentParser(description='Apple Health Export Analyzer Pro')
    parser.add_argument('--export_dir', required=True, help='Path to apple_health_export folder')
    parser.add_argument('--start_date', help='YYYY-MM-DD to filter recent data (e.g. 2025-11-30)')
    args = parser.parse_args()
    
    export_xml = os.path.join(args.export_dir, '导出.xml')
    gpx_dir = os.path.join(args.export_dir, 'workout-routes')
    
    print("\n[1] Parsing Main Export Data (This may take a minute)...")
    if os.path.exists(export_xml):
        data = analyze_export(export_xml, args.start_date)
        
        # Steps
        steps = list(data['steps'].values())
        if steps:
            print(f"-> Average Daily Steps: {sum(steps)/len(steps):.0f} ({len(steps)} days recorded)")
            
        # RHR & VO2Max
        if data['rhr']:
            print(f"-> Average Resting HR: {sum(data['rhr'])/len(data['rhr']):.1f} bpm")
        if data['vo2max']:
            print(f"-> Average VO2Max: {sum(data['vo2max'])/len(data['vo2max']):.2f} mL/kg/min")
            
        # Calories & Steadiness
        if data['burn']:
             print(f"-> Active Calories Burned (Avg): {sum(data['burn'])/len(data['burn']):.0f} kcal/day")
        if data['steadiness']:
             avg_steady = sum(data['steadiness'])/len(data['steadiness'])
             print(f"-> Walking Steadiness: {avg_steady*100:.1f}% ({'OK' if avg_steady > 0.5 else 'RISK'})")
    else:
        print("-> Error: 导出.xml not found.")

    print("\n[2] Parsing GPS Workouts (For Joint/Elevation checks)...")
    workouts = analyze_gpx(gpx_dir)
    if workouts:
        avg_dist = sum(w['dist_km'] for w in workouts) / len(workouts)
        avg_ele = sum(w['ele_gain'] for w in workouts) / len(workouts)
        print(f"-> Total GPS Workouts: {len(workouts)}")
        print(f"-> Average Distance per workout: {avg_dist:.2f} km")
        print(f"-> Average Elevation Gain: {avg_ele:.1f} meters (Watch out for elevator altimeter bugs!)")
        
    print("\n=== Analysis Complete ===")

if __name__ == "__main__":
    main()

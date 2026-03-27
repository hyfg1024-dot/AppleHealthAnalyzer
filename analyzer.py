import xml.etree.ElementTree as ET
import os
import math
import sys
import argparse
from datetime import datetime

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
        try:
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
        except Exception:
            pass
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

def generate_report(export_dir, start_date=None):
    export_xml = os.path.join(export_dir, '导出.xml')
    if not os.path.exists(export_xml):
        export_xml = os.path.join(export_dir, 'export.xml') # Try english fallback
        
    gpx_dir = os.path.join(export_dir, 'workout-routes')
    
    report = []
    
    report.append("[1] Parsing Main Export Data (This may take a minute)...")
    if os.path.exists(export_xml):
        data = analyze_export(export_xml, start_date)
        
        steps = list(data['steps'].values())
        if steps:
            report.append(f"-> Average Daily Steps: {sum(steps)/len(steps):.0f} ({len(steps)} days recorded)")
            
        if data['rhr']:
            report.append(f"-> Average Resting HR: {sum(data['rhr'])/len(data['rhr']):.1f} bpm")
        if data['vo2max']:
            report.append(f"-> Average VO2Max: {sum(data['vo2max'])/len(data['vo2max']):.2f} mL/kg/min")
            
        if data['burn']:
            report.append(f"-> Active Calories Burned (Avg): {sum(data['burn'])/len(data['burn']):.0f} kcal/day")
        if data['steadiness']:
             avg_steady = sum(data['steadiness'])/len(data['steadiness'])
             report.append(f"-> Walking Steadiness: {avg_steady*100:.1f}% ({'OK' if avg_steady > 0.5 else 'RISK'})")
    else:
        return "Error: 导出.xml or export.xml not found in the selected folder.\n请检查是否选错了文件夹，或者该文件夹内未包含 '导出.xml' 或 'export.xml'。"

    report.append("\n[2] Parsing GPS Workouts (For Joint/Elevation checks)...")
    workouts = analyze_gpx(gpx_dir)
    if workouts:
        avg_dist = sum(w['dist_km'] for w in workouts) / len(workouts)
        avg_ele = sum(w['ele_gain'] for w in workouts) / len(workouts)
        report.append(f"-> Total GPS Workouts: {len(workouts)}")
        report.append(f"-> Average Distance per workout: {avg_dist:.2f} km")
        report.append(f"-> Average Elevation Gain: {avg_ele:.1f} meters (Watch out for elevator altimeter bugs!)")
    else:
        report.append("-> No GPS workouts found.")
        
    report.append("\n=== Analysis Complete ===")
    return "\n".join(report)

def run_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
    import threading

    root = tk.Tk()
    root.title("Apple Health Analyzer (苹果健康数据分析器)")
    root.geometry("750x550")
    
    # GUI state
    filter_recent_var = tk.BooleanVar(value=True)

    def process_folder(folder_selected, use_recent):
        try:
            # Default to filtering the last 120 days if checkbox is ticked
            start_date_str = None
            if use_recent:
               import datetime
               start_date_str = (datetime.datetime.now() - datetime.timedelta(days=120)).strftime("%Y-%m-%d")

            report_str = generate_report(folder_selected, start_date=start_date_str)
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, report_str)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse data:\n{str(e)}")
        finally:
            btn.config(state=tk.NORMAL)
            btn.config(text="📁 Browse Apple Health Export Folder\n(选择解压后的导出文件夹)")

    def select_folder():
        folder_selected = filedialog.askdirectory(title="Select Apple Health Export Folder")
        if folder_selected:
            btn.config(state=tk.DISABLED)
            btn.config(text="Processing... Please wait 1-2 minutes...")
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, "Reading massive XML file. Your application might freeze temporarily. Please wait...\n\n(正在流式解析数十吉节的海量健康数据，请耐心等待1-2分钟...)\n")
            root.update()
            
            use_recent = filter_recent_var.get()
            
            # Run in background to prevent GUI freeze
            threading.Thread(target=process_folder, args=(folder_selected, use_recent), daemon=True).start()

    # Layout
    top_frame = tk.Frame(root)
    top_frame.pack(pady=20)
    
    btn = tk.Button(top_frame, text="📁 Browse Apple Health Export Folder\n(选择解压后的导出文件夹)", 
                    command=select_folder, font=('Arial', 14), pady=10, padx=20)
    btn.pack()
    
    chk = tk.Checkbutton(top_frame, text="Only analyze the last 120 days (Recommended to avoid old device pollution)\n(仅分析最近 120 天的数据，极其推荐勾选)", 
                         variable=filter_recent_var, font=('Arial', 12))
    chk.pack(pady=10)

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=('Courier', 13), bg="#1e1e1e", fg="#00ff00")
    text_area.pack(expand=True, fill='both', padx=20, pady=10)
    
    # Welcome message
    text_area.insert(tk.END, "Welcome to Apple Health Analyzer!\n\n1. Export your Health Data from iPhone.\n2. Unzip 'export.zip' or '导出.zip'.\n3. Click the button above and select the unzipped folder.\n\n(欢迎跑库！请直接点击上方按钮，选择你刚刚解压好的 apple_health_export 文件夹即可开始全自动分析。由于数据通常高达几GB，点击运行后系统可能会稍微卡顿读取，请不用担心，倒杯水回来就出结果了。)\n")

    root.mainloop()

def main():
    # If arguments are provided, run as CLI. Otherwise, popup GUI.
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='Apple Health Export Analyzer Pro')
        parser.add_argument('--export_dir', required=True, help='Path to apple_health_export folder')
        parser.add_argument('--start_date', help='YYYY-MM-DD to filter recent data (e.g. 2025-11-30)')
        args = parser.parse_args()
        
        print(generate_report(args.export_dir, args.start_date))
    else:
        run_gui()

if __name__ == "__main__":
    main()

# Apple Health Data Discovery & Analyzer

A highly optimized, un-opinionated Python script designed to parse large Apple Health Export XML files (`导出.xml`) natively and efficiently. 

This tool is specifically built to handle massive Apple Health databases (up to tens of gigabytes) without crashing your system's RAM. It uses Python's `xml.etree.ElementTree.iterparse` to stream the data, extracting your hidden physiological and workout baselines into a compact, human-readable terminal report.

## 🚀 Features

- **Streaming Parser**: Bypasses standard memory limits by reading the XML chunk by chunk.
- **GPS Elevation Trap Detection**: Automatically loops through `.gpx` files in the `workout-routes` directory to calculate absolute elevation gain (useful for spotting "elevator altitude tracking" bugs or knee-stress risks).
- **Core Vitals & Medical Baselines**: Condenses thousands of Resting Heart Rate (RHR), VO2Max, and Fall Risk (Walking Steadiness) records into distinct averages.
- **Active Caloric Burn**: Aggregates Activity Summary rings to report your absolute daily extra calorie burn.

## 📦 Installation

No external dependencies are required! The script relies entirely on Python 3 Standard Library.

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/AppleHealthAnalyzer.git
   ```
2. Export your Apple Health Data from your iPhone (Health App -> Profile -> Export All Health Data).
3. Unzip the `export.zip` folder on your computer.

## 🛠️ Usage

Simply point the script to the unzipped Apple Health export folder. You can optionally provide a `--start_date` to filter out old or "polluted" historical data (e.g., from older Apple Watches).

```bash
# Basic usage
python3 analyzer.py --export_dir </path/to/apple_health_export>

# Filter for recent data only (Highly Recommended)
python3 analyzer.py --export_dir </path/to/apple_health_export> --start_date 2025-11-30
```

## 📊 Example Output

```text
[1] Parsing Main Export Data (This may take a minute)...
-> Average Daily Steps: 10450 (100 days recorded)
-> Average Resting HR: 60.5 bpm
-> Average VO2Max: 42.15 mL/kg/min
-> Active Calories Burned (Avg): 610 kcal/day
-> Walking Steadiness: 94.2% (OK)

[2] Parsing GPS Workouts (For Joint/Elevation checks)...
-> Total GPS Workouts: 59
-> Average Distance per workout: 2.42 km
-> Average Elevation Gain: 169.5 meters (Watch out for elevator altimeter bugs!)

=== Analysis Complete ===
```

## Contributing
Feel free to open issues or submit Pull Requests for adding parsing logic to more esoteric Apple Health XML `<Record type="HKQuantityTypeIdentifier...">` types.

## License
MIT License.

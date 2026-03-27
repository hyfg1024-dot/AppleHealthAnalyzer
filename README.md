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

---

# Apple Health 数据发掘与分析家 (中文版)

这是一个高度优化、纯净解耦的 Python 脚本，专门用于原生、高效地解析庞大的 Apple Health 导出数据 (`导出.xml`)。

本工具专为处理海量 Apple Health 数据库（最高可达几十 GB）而生，彻底告别内存爆炸死机。它使用了 Python 原生的 `xml.etree.ElementTree.iterparse` 进行流式读取，能够从你的 XML 迷宫中提炼出隐藏的核心生理体征与运动基线，并生成一张极其紧凑易读的终端报告。

## 🚀 核心特性

- **流式解析架构**：原生避开内存瓶颈限制，按块读取 XML，你的硬盘有多大，它就能解析多大。
- **GPS 爬坡陷阱检测**：自动遍历 `workout-routes` 目录下的 `.gpx` 轨迹文件，计算真实的绝对海拔爬升量（完美识别“戴着手表坐电梯”导致的虚假爬楼层 Bug，排查膝盖受损风险）。
- **硬核生命体征基调**：将成千上万条“静息心率 (RHR)”、“最大摄氧量 (VO2Max)”以及“步行稳定性”数据进行精准的周期均值压缩。
- **活动卡路里闭环**：聚合“健身记录圆环 (Activity Summary)”中的主动消耗数据（千卡），直观展现你的真实额外热量缺口。

## 📦 安装指南

完全不需要安装任何第三方依赖！仅仅依赖 Python 3 标准库。

1. 克隆此仓库：
   ```bash
   git clone https://github.com/hyfg1024-dot/AppleHealthAnalyzer.git
   ```
2. 从你的 iPhone 中导出 Apple 健康数据（健康 App -> 右上角头像 -> 导出所有健康数据）。
3. 将发送到电脑的 `export.zip` 解压。

## 🛠️ 如何使用

直接让脚本指向解压后的 Apple Health 导出文件夹。你还可以选填 `--start_date` 来过滤掉手机时代久远的历史残留数据（极其推荐，防止被旧设备拉低了现在的运动平均值）。

```bash
# 基础用法
python3 analyzer.py --export_dir </你的路径/apple_health_export>

# 只看近期的运动基数（强推用法）
python3 analyzer.py --export_dir </你的路径/apple_health_export> --start_date 2025-11-30
```

## 📊 运行结果演示

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

## 贡献与共建
欢迎随时提交 Issue 或发起 PR。Apple Health 的 `<Record type="HKQuantityTypeIdentifier...">` 标签库浩如烟海，如果你想添加更多极其冷门的医学指标解析逻辑，请放手去改。

## 开源协议
MIT License.

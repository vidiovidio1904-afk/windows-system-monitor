# Windows System Monitor Pro

Real-time system monitoring utility for Windows with a modern dark UI.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

* 📊 **Summary** — host, OS, CPU model, RAM, uptime
* 🖥 **CPU** — total load, per-core load, frequency
* 🧠 **Memory** — RAM and swap usage
* 🎮 **GPU** — NVIDIA cards via NVML (load, VRAM, temperature)
* 🌡 **Temperatures** — sensors via psutil / WMI
* 💽 **Disks** — partitions usage and total I/O counters
* 🌐 **Network** — traffic totals, interfaces, active connections
* ⚙ **Processes** — full process list with users
* 🔥 **Top processes** — sorted by RAM usage
* 📈 **Live graphs** — CPU/RAM history (last 60 seconds)
* 📄 **HTML report** — one-click full system report (`report.html`)
* 🔄 Real-time metric cards updated every second
* 🌙 Dark theme (CustomTkinter)

## Screenshot

*(add screenshot here)*

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

> **Tip:** run as Administrator for full process list, active connections
> and temperature sensors.

## Build EXE

```bash
pip install pyinstaller
build.bat
```

Or download the ready artifact from
[GitHub Actions](../../actions) (built on every push to `main`).

## Technologies

* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — modern UI
* [psutil](https://github.com/giampaolo/psutil) — system metrics
* [GPUtil](https://github.com/anderskm/gpututil) — NVIDIA GPU stats
* [Matplotlib](https://matplotlib.org/) — live graphs
* WMI — temperature sensors fallback on Windows

## Project structure

```
├── main.py                  # application (helpers + GUI)
├── tests/test_helpers.py    # unit tests for helpers
├── build.bat                # PyInstaller build script
├── .github/workflows/build.yml  # CI: build EXE artifact
└── requirements.txt
```

## Testing

```bash
pip install pytest
pytest
```

## Notes

* GPU monitoring requires an NVIDIA GPU (NVML library).
* Temperature sensors availability depends on your motherboard —
  run as Administrator for WMI thermal zones.

## Author

Alex

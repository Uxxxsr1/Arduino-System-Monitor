# Arduino-System-Monitor

A PC resource monitoring system that displays real-time CPU, RAM, GPU usage, and network speed on an Arduino LCD Keypad Shield. The PC side collects system statistics using Python and sends the data over a serial connection to an Arduino, which updates the display.

🧩 Features
Displays CPU, RAM, GPU usage.

GPU temperature and fan speed monitoring.

Real-time download and upload speed.

Menu navigation via LCD Shield buttons.

Python GUI for status display and control.

⚙️ Requirements
On the PC:
Python 3.8+

Python packages:

bash
Копировать
Редактировать
pip install psutil pyserial pynvml
Connected Arduino with an LCD Keypad Shield.

On the Arduino:
Arduino Uno/Nano with LCD Keypad Shield.

Uploaded sketch for reading serial data and displaying stats.

📦 Installation & Usage
1. Upload Arduino Sketch
Use the Arduino IDE to upload the provided sketch:

cpp
Копировать
Редактировать
#include <LiquidCrystal.h>
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);
// ...
See arduino_monitor.ino for the full code.

2. Run the Python App
bash
Копировать
Редактировать
python monitor_app.py
The GUI will open, detect the Arduino automatically, and begin sending system data every 0.5 seconds.

🖼️ Display Screens
There are 3 screens you can navigate using the Left and Right buttons on the LCD Shield:

📊 Screen 1: System Load
makefile
Копировать
Редактировать
CPU:35.4% R:48.2%
GPU:27.1% 54.0°C
🌀 Screen 2: Cooling
makefile
Копировать
Редактировать
Fan Speed
GPU:45.0% CPU:3.5%
🌐 Screen 3: Network
bash
Копировать
Редактировать
Network
D:123.4 U:56.7 KB/s
🛠️ Project Structure
bash
Копировать
Редактировать
/arduino_monitor.ino        — Arduino sketch (C++)
/monitor_app.py             — Python GUI app
/README.md                  — This file
/app.ico                    — Optional icon for EXE build
🧾 Notes
GPU data is retrieved using pynvml (for NVIDIA cards only).

CPU fan speed is estimated based on CPU load (if no direct sensor is available).

The app auto-detects the Arduino COM port.
🧑‍💻 Author
Created by [Uxxxsr1]
Contributions and issues are welcome!

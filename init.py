import serial
import serial.tools.list_ports
import psutil
import time
from tkinter import Tk, Frame, Label, StringVar, Button, ttk
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetUtilizationRates, \
    nvmlDeviceGetTemperature, nvmlDeviceGetFanSpeed, nvmlShutdown, NVML_TEMPERATURE_GPU

class ArduinoMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino System Monitor")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Переменные для данных
        self.cpu_var = StringVar(value="0%")
        self.ram_var = StringVar(value="0%")
        self.gpu_load_var = StringVar(value="0%")
        self.gpu_temp_var = StringVar(value="0°C")
        self.fan_speed_var = StringVar(value="0%")
        self.download_var = StringVar(value="0 KB/s")
        self.upload_var = StringVar(value="0 KB/s")
        self.connection_status = StringVar(value="Отключено")
        self.port_var = StringVar(value="Не найдено")

        # Стили
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0", font=('Arial', 10))
        self.style.configure("Header.TLabel", font=('Arial', 12, 'bold'))
        self.style.configure("Value.TLabel", font=('Arial', 14))
        self.style.configure("Status.TLabel", font=('Arial', 10, 'italic'))
        self.style.configure("Red.TLabel", foreground="red")
        self.style.configure("Green.TLabel", foreground="green")

        # Основные фреймы
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill="both", expand=True)

        self.create_header()
        self.create_stats_section()
        self.create_connection_section()
        self.create_controls()

        # Инициализация соединения
        self.ser = None
        self.running = False
        self.find_and_connect()

    def format_speed(self, speed_kb):
        """Форматирует скорость сети в удобочитаемый вид (KB/s или MB/s)"""
        if speed_kb < 1024:  # Меньше 1 MB
            return f"{speed_kb:.1f} KB/s"
        else:
            return f"{speed_kb / 1024:.1f} MB/s"

    def create_header(self):
        header = ttk.Frame(self.main_frame)
        header.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header, text="Arduino System Monitor", style="Header.TLabel").pack()

    def create_stats_section(self):
        stats_frame = ttk.Frame(self.main_frame)
        stats_frame.pack(fill="x", pady=10)

        # CPU
        self.create_stat_row(stats_frame, "Процессор:", self.cpu_var)
        # RAM
        self.create_stat_row(stats_frame, "Оперативная память:", self.ram_var)
        # GPU Load
        self.create_stat_row(stats_frame, "Графический процессор:", self.gpu_load_var)
        # GPU Temp
        self.create_stat_row(stats_frame, "Температура GPU:", self.gpu_temp_var)
        # Fan Speed
        self.create_stat_row(stats_frame, "Скорость вентилятора:", self.fan_speed_var)
        # Network Download
        self.create_stat_row(stats_frame, "Скорость загрузки:", self.download_var)
        # Network Upload
        self.create_stat_row(stats_frame, "Скорость отдачи:", self.upload_var)

    def create_stat_row(self, parent, label_text, var):
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=2)
        
        ttk.Label(row, text=label_text, width=25, anchor="w").pack(side="left")
        ttk.Label(row, textvariable=var, style="Value.TLabel").pack(side="left")

    def create_connection_section(self):
        conn_frame = ttk.Frame(self.main_frame)
        conn_frame.pack(fill="x", pady=20)

        ttk.Label(conn_frame, text="Статус подключения:", style="Header.TLabel").pack(anchor="w")
        
        status_row = ttk.Frame(conn_frame)
        status_row.pack(fill="x", pady=5)
        
        ttk.Label(status_row, text="Порт:").pack(side="left")
        ttk.Label(status_row, textvariable=self.port_var).pack(side="left", padx=10)
        
        ttk.Label(status_row, text="Статус:").pack(side="left", padx=(20, 0))
        self.status_label = ttk.Label(status_row, textvariable=self.connection_status)
        self.status_label.pack(side="left")

    def create_controls(self):
        ctrl_frame = ttk.Frame(self.main_frame)
        ctrl_frame.pack(fill="x", pady=10)
        
        self.start_btn = ttk.Button(ctrl_frame, text="Старт", command=self.start_monitoring)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(ctrl_frame, text="Стоп", command=self.stop_monitoring, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        ttk.Button(ctrl_frame, text="Переподключиться", command=self.reconnect).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Выход", command=self.root.quit).pack(side="right")

    def update_connection_status(self, connected, port=None):
        if connected:
            self.connection_status.set("Подключено")
            self.status_label.config(style="Green.TLabel")
            self.port_var.set(port)
        else:
            self.connection_status.set("Отключено")
            self.status_label.config(style="Red.TLabel")
            self.port_var.set("Не найдено")

    def find_and_connect(self):
        port = self.find_arduino_port()
        if port:
            try:
                if self.ser and self.ser.is_open:
                    self.ser.close()
                
                self.ser = serial.Serial(port, 9600, timeout=1.0, write_timeout=1.0)
                time.sleep(2)  # Ожидание инициализации
                self.update_connection_status(True, port)
                return True
            except Exception as e:
                print(f"Ошибка подключения: {e}")
        
        self.update_connection_status(False)
        return False

    def find_arduino_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description or "Leonardo" in port.description:
                return port.device
        return None

    def get_gpu_info(self):
        try:
            nvmlInit()
            handle = nvmlDeviceGetHandleByIndex(0)

            utilization = nvmlDeviceGetUtilizationRates(handle)
            temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
            fan = nvmlDeviceGetFanSpeed(handle)

            nvmlShutdown()

            return utilization.gpu, temp, fan
        except Exception as e:
            print(f"GPU NVML error: {e}")
            return 0, 0, 0

    def start_monitoring(self):
        if not self.ser or not self.ser.is_open:
            if not self.find_and_connect():
                return

        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        self.prev_net = psutil.net_io_counters()
        self.prev_time = time.time()
        
        self.monitor_loop()

    def stop_monitoring(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def reconnect(self):
        self.stop_monitoring()
        self.find_and_connect()

    def monitor_loop(self):
        if not self.running:
            return

        current_time = time.time()
        dt = current_time - self.prev_time

        # Получение данных
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        gpu_load, gpu_temp, fan_speed = self.get_gpu_info()

        # Расчет скорости сети
        net_io = psutil.net_io_counters()
        download_speed_kb = (net_io.bytes_recv - self.prev_net.bytes_recv) / 1024 / dt
        upload_speed_kb = (net_io.bytes_sent - self.prev_net.bytes_sent) / 1024 / dt

        self.prev_net = net_io
        self.prev_time = current_time

        # Обновление интерфейса
        self.cpu_var.set(f"{cpu:.1f}%")
        self.ram_var.set(f"{ram:.1f}%")
        self.gpu_load_var.set(f"{gpu_load:.1f}%")
        self.gpu_temp_var.set(f"{gpu_temp:.1f}°C")
        self.fan_speed_var.set(f"{fan_speed:.1f}%")
        self.download_var.set(self.format_speed(download_speed_kb))
        self.upload_var.set(self.format_speed(upload_speed_kb))

        # Отправка данных на Arduino (в KB/s)
        if self.ser and self.ser.is_open:
            try:
                data = f"{cpu:.1f},{ram:.1f},{gpu_load:.1f},{gpu_temp:.1f},{fan_speed:.1f},{download_speed_kb:.1f},{upload_speed_kb:.1f}\n"
                self.ser.write(data.encode('utf-8'))
            except Exception as e:
                print(f"Ошибка отправки данных: {e}")
                self.update_connection_status(False)

        # Планирование следующего обновления
        self.root.after(500, self.monitor_loop)

if __name__ == "__main__":
    root = Tk()
    app = ArduinoMonitorApp(root)
    root.mainloop()
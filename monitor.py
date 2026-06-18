import tkinter as tk
from tkinter import messagebox, filedialog
import psutil
import GPUtil
import datetime
import platform
import socket


class SystemMonitor:

    def __init__(self, root):
        self.root = root

        self.root.title("Windows System Monitor v1.1")
        self.root.geometry("500x420")
        self.root.resizable(False, False)

        title = tk.Label(
            root,
            text="Windows System Monitor v1.1",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)

        self.info = tk.Label(
            root,
            text="Loading...",
            justify="left",
            font=("Consolas", 11)
        )

        self.info.pack(pady=10)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Refresh",
            width=15,
            command=self.update_stats
        ).grid(row=0, column=0, padx=5)

        tk.Button(
            button_frame,
            text="Export Report",
            width=15,
            command=self.export_report
        ).grid(row=0, column=1, padx=5)

        self.update_stats()

    def get_uptime(self):
        boot = datetime.datetime.fromtimestamp(psutil.boot_time())
        now = datetime.datetime.now()

        uptime = now - boot

        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60

        return f"{days}d {hours}h {minutes}m"

    def get_gpu_info(self):
        try:
            gpus = GPUtil.getGPUs()

            if not gpus:
                return "Not Found", "N/A", "N/A"

            gpu = gpus[0]

            usage = f"{gpu.load * 100:.0f}%"
            temp = f"{gpu.temperature}°C"

            return gpu.name, usage, temp

        except Exception:
            return "Error", "N/A", "N/A"

    def get_cpu_temp(self):
        try:
            temps = psutil.sensors_temperatures()

            if not temps:
                return "N/A"

            for name in temps:
                if temps[name]:
                    return f"{temps[name][0].current}°C"

            return "N/A"

        except Exception:
            return "N/A"

    def update_stats(self):

        cpu = psutil.cpu_percent()

        ram = psutil.virtual_memory()

        disk = psutil.disk_usage("/")

        hostname = socket.gethostname()

        os_name = platform.system() + " " + platform.release()

        cpu_temp = self.get_cpu_temp()

        gpu_name, gpu_usage, gpu_temp = self.get_gpu_info()

        text = f"""
🖥 Computer: {hostname}

💻 OS: {os_name}

⚙ CPU Usage: {cpu}%
🌡 CPU Temp: {cpu_temp}

🧠 RAM Usage: {ram.percent}%

📀 Disk Usage: {disk.percent}%

🎮 GPU: {gpu_name}
📈 GPU Usage: {gpu_usage}
🌡 GPU Temp: {gpu_temp}

⏱ Uptime: {self.get_uptime()}
"""

        self.info.config(text=text)

        self.root.after(2000, self.update_stats)

    def export_report(self):

        cpu = psutil.cpu_percent()

        ram = psutil.virtual_memory()

        disk = psutil.disk_usage("/")

        gpu_name, gpu_usage, gpu_temp = self.get_gpu_info()

        report = f"""
Windows System Monitor Report

Date: {datetime.datetime.now()}

CPU Usage: {cpu}%
CPU Temp: {self.get_cpu_temp()}

RAM Usage: {ram.percent}%

Disk Usage: {disk.percent}%

GPU: {gpu_name}
GPU Usage: {gpu_usage}
GPU Temp: {gpu_temp}

Uptime: {self.get_uptime()}
"""

        file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt")]
        )

        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(report)

            messagebox.showinfo(
                "Success",
                "Report exported successfully"
            )


if __name__ == "__main__":

    root = tk.Tk()

    app = SystemMonitor(root)

    root.mainloop()

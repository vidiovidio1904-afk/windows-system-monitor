import tkinter as tk
from tkinter import ttk
import platform
import socket
import psutil


class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows System Monitor Pro v2.0")
        self.root.geometry("1000x600")

        self.create_ui()
        self.update_info()

    def create_ui(self):

        self.left_frame = tk.Frame(self.root, width=250, bg="#f0f0f0")
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.tree = ttk.Treeview(self.left_frame)
        self.tree.pack(fill="both", expand=True)

        self.tree.insert("", "end", "summary", text="📊 Сводка")
        self.tree.insert("", "end", "cpu", text="🖥 Процессор")
        self.tree.insert("", "end", "ram", text="💾 Память")
        self.tree.insert("", "end", "gpu", text="🎮 Видеокарта")
        self.tree.insert("", "end", "disk", text="📁 Накопители")
        self.tree.insert("", "end", "network", text="🌐 Сеть")
        self.tree.insert("", "end", "processes", text="⚙ Процессы")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.title_label = tk.Label(
            self.right_frame,
            text="Сводка системы",
            font=("Segoe UI", 18, "bold")
        )
        self.title_label.pack(pady=10)

        self.info_text = tk.Text(
            self.right_frame,
            font=("Consolas", 11)
        )
        self.info_text.pack(fill="both", expand=True, padx=10, pady=10)

    def on_select(self, event):

        selected = self.tree.selection()[0]

        if selected == "summary":
            self.show_summary()

        elif selected == "cpu":
            self.show_cpu()

        elif selected == "ram":
            self.show_ram()

        elif selected == "disk":
            self.show_disk()

        elif selected == "network":
            self.show_network()

        elif selected == "processes":
            self.show_processes()

        elif selected == "gpu":
            self.show_gpu()

    def clear_text(self):
        self.info_text.delete("1.0", tk.END)

    def show_summary(self):

        self.title_label.config(text="Сводка системы")

        self.clear_text()

        text = f"""
Компьютер: {socket.gethostname()}

ОС: {platform.system()} {platform.release()}

Процессор:
{platform.processor()}

CPU:
{psutil.cpu_percent()} %

RAM:
{psutil.virtual_memory().percent} %

Время работы:
{round(psutil.boot_time())}
"""

        self.info_text.insert(tk.END, text)

    def show_cpu(self):

        self.title_label.config(text="Процессор")

        self.clear_text()

        text = f"""
Ядер: {psutil.cpu_count(logical=False)}

Потоков: {psutil.cpu_count()}

Загрузка:
{psutil.cpu_percent()} %
"""

        self.info_text.insert(tk.END, text)

    def show_ram(self):

        mem = psutil.virtual_memory()

        self.title_label.config(text="Оперативная память")

        self.clear_text()

        text = f"""
Всего:
{round(mem.total / 1024**3,2)} GB

Используется:
{round(mem.used / 1024**3,2)} GB

Свободно:
{round(mem.available / 1024**3,2)} GB

Загрузка:
{mem.percent} %
"""

        self.info_text.insert(tk.END, text)

    def show_disk(self):

        self.title_label.config(text="Накопители")

        self.clear_text()

        text = ""

        for p in psutil.disk_partitions():

            try:
                usage = psutil.disk_usage(p.mountpoint)

                text += f"""
Диск: {p.device}

Всего:
{round(usage.total / 1024**3,2)} GB

Использовано:
{usage.percent} %

-----------------------
"""

            except:
                pass

        self.info_text.insert(tk.END, text)

    def show_network(self):

        net = psutil.net_io_counters()

        self.title_label.config(text="Сеть")

        self.clear_text()

        text = f"""
Отправлено:
{round(net.bytes_sent / 1024**2,2)} MB

Получено:
{round(net.bytes_recv / 1024**2,2)} MB
"""

        self.info_text.insert(tk.END, text)

    def show_processes(self):

        self.title_label.config(text="Процессы")

        self.clear_text()

        text = ""

        for proc in psutil.process_iter(['pid', 'name']):

            try:
                text += f"{proc.info['pid']} | {proc.info['name']}\n"

            except:
                pass

        self.info_text.insert(tk.END, text)

    def show_gpu(self):

        self.title_label.config(text="Видеокарта")

        self.clear_text()

        self.info_text.insert(
            tk.END,
            "GPU раздел будет добавлен на следующем этапе"
        )

    def update_info(self):

        selected = self.tree.selection()

        if selected:
            self.on_select(None)

        self.root.after(2000, self.update_info)


root = tk.Tk()
app = SystemMonitor(root)
root.mainloop()

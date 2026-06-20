import customtkinter as ctk
import psutil
import platform
import socket
from collections import deque

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SystemMonitor:

```
def __init__(self):

    self.root = ctk.CTk()
    self.root.title("Windows System Monitor Pro")
    self.root.geometry("1600x900")

    self.cpu_history = deque(maxlen=60)
    self.ram_history = deque(maxlen=60)

    for _ in range(60):
        self.cpu_history.append(0)
        self.ram_history.append(0)

    self.build_ui()

    self.root.after(1000, self.update_stats)

    self.show_summary()

    self.root.mainloop()

def build_ui(self):

    self.sidebar = ctk.CTkFrame(
        self.root,
        width=250,
        corner_radius=0
    )

    self.sidebar.pack(
        side="left",
        fill="y"
    )

    ctk.CTkLabel(
        self.sidebar,
        text="SYSTEM MONITOR",
        font=("Segoe UI", 24, "bold")
    ).pack(pady=20)

    menu = [
        ("Сводка", self.show_summary),
        ("CPU", self.show_cpu),
        ("RAM", self.show_ram),
        ("Диски", self.show_disks),
        ("Сеть", self.show_network),
        ("Графики", self.show_graphs)
    ]

    for text, command in menu:

        ctk.CTkButton(
            self.sidebar,
            text=text,
            command=command,
            height=40
        ).pack(
            fill="x",
            padx=10,
            pady=5
        )

    self.main = ctk.CTkFrame(self.root)

    self.main.pack(
        side="right",
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

    self.cards = ctk.CTkFrame(self.main)
    self.cards.pack(fill="x", padx=10, pady=10)

    self.cpu_label = ctk.CTkLabel(
        self.cards,
        text="CPU: 0%",
        font=("Segoe UI", 22, "bold")
    )

    self.cpu_label.pack(
        side="left",
        padx=20
    )

    self.ram_label = ctk.CTkLabel(
        self.cards,
        text="RAM: 0%",
        font=("Segoe UI", 22, "bold")
    )

    self.ram_label.pack(
        side="left",
        padx=20
    )

    self.disk_label = ctk.CTkLabel(
        self.cards,
        text="DISK: 0%",
        font=("Segoe UI", 22, "bold")
    )

    self.disk_label.pack(
        side="left",
        padx=20
    )

    self.content = ctk.CTkTextbox(
        self.main,
        font=("Consolas", 14)
    )

    self.content.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=10
    )

```
def set_content(self, text):

    self.content.delete("1.0", "end")
    self.content.insert("1.0", text)

def show_summary(self):

    text = f"""
```

Компьютер: {socket.gethostname()}

Система:
{platform.system()} {platform.release()}

Процессор:
{platform.processor()}

Физических ядер:
{psutil.cpu_count(logical=False)}

Логических потоков:
{psutil.cpu_count()}

Оперативная память:
{round(psutil.virtual_memory().total / 1024**3, 1)} GB
"""

```
    self.set_content(text)

def show_cpu(self):

    text = f"""
```

Загрузка CPU: {psutil.cpu_percent()} %

Ядер:
{psutil.cpu_count(logical=False)}

Потоков:
{psutil.cpu_count()}
"""

```
    self.set_content(text)

def show_ram(self):

    mem = psutil.virtual_memory()

    text = f"""
```

Всего памяти:
{round(mem.total / 1024**3, 1)} GB

Используется:
{round(mem.used / 1024**3, 1)} GB

Свободно:
{round(mem.available / 1024**3, 1)} GB

Загрузка:
{mem.percent} %
"""

```
    self.set_content(text)

def show_disks(self):

    text = ""

    for p in psutil.disk_partitions():

        try:

            usage = psutil.disk_usage(p.mountpoint)

            text += f"""
```

Диск: {p.device}

Всего:
{round(usage.total / 1024**3, 1)} GB

Использовано:
{round(usage.used / 1024**3, 1)} GB

Свободно:
{round(usage.free / 1024**3, 1)} GB

Загрузка:
{usage.percent} %

---

"""

```
        except:
            pass

    self.set_content(text)

def show_network(self):

    net = psutil.net_io_counters()

    text = f"""
```

Отправлено:
{round(net.bytes_sent / 1024**2, 2)} MB

Получено:
{round(net.bytes_recv / 1024**2, 2)} MB
"""


    self.set_content(text)

```
def update_stats(self):

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    try:
        disk = psutil.disk_usage("C:\\").percent
    except:
        disk = 0

    self.cpu_label.configure(
        text=f"CPU: {cpu:.1f}%"
    )

    self.ram_label.configure(
        text=f"RAM: {ram:.1f}%"
    )

    self.disk_label.configure(
        text=f"DISK: {disk:.1f}%"
    )

    self.cpu_history.append(cpu)
    self.ram_history.append(ram)

    self.root.after(
        1000,
        self.update_stats
    )

def show_graphs(self):

    self.create_graph_window()

def create_graph_window(self):

    graph_window = ctk.CTkToplevel(
        self.root
    )

    graph_window.title(
        "CPU / RAM Graph"
    )

    graph_window.geometry(
        "1000x500"
    )

    figure = Figure(
        figsize=(10, 5),
        dpi=100
    )

    ax = figure.add_subplot(111)

    canvas = FigureCanvasTkAgg(
        figure,
        master=graph_window
    )

    canvas.get_tk_widget().pack(
        fill="both",
        expand=True
    )

    def update_graph():

        ax.clear()

        ax.plot(
            list(self.cpu_history),
            label="CPU %"
        )

        ax.plot(
            list(self.ram_history),
            label="RAM %"
        )

        ax.set_ylim(0, 100)

        ax.set_title(
            "Real Time Monitoring"
        )

        ax.legend()

        canvas.draw()

        graph_window.after(
            1000,
            update_graph
        )

            update_graph()


if __name__ == "__main__":
    SystemMonitor()


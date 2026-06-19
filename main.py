import customtkinter as ctk
import psutil
import platform
import socket
import time
import threading
from collections import deque

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

try:
    import GPUtil
except:
    GPUtil = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SystemMonitor:

    def __init__(self):

        self.root = ctk.CTk()

        self.root.title("Windows System Monitor Pro v7.0")
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
            width=260,
            corner_radius=0
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="🖥 SYSTEM MONITOR",
            font=("Segoe UI", 24, "bold")
        )

        self.logo.pack(pady=25)

        menu = [

            ("📊 Сводка", self.show_summary),

            ("🖥 Процессор", self.show_cpu),

            ("🧠 Память", self.show_ram),

            ("🎮 Видеокарта", self.show_gpu),

            ("🌡 Температура CPU", self.show_cpu_temp),

            ("💽 Диски", self.show_disks),

            ("🌐 Сеть", self.show_network),

            ("⚙ Процессы", self.show_processes),

            ("🔥 ТОП процессов", self.show_top_processes),

            ("📈 Графики", self.show_graphs)

        ]

        for text, command in menu:

            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                height=42,
                command=command
            )

            btn.pack(
                fill="x",
                padx=10,
                pady=4
            )

        self.main = ctk.CTkFrame(self.root)

        self.main.pack(
            side="right",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.header = ctk.CTkLabel(
            self.main,
            text="📊 Системный монитор",
            font=("Segoe UI", 34, "bold")
        )

        self.header.pack(pady=15)

        self.cards = ctk.CTkFrame(self.main)

        self.cards.pack(
            fill="x",
            padx=10
        )

        self.cpu_card = ctk.CTkFrame(self.cards)
        self.cpu_card.pack(
            side="left",
            expand=True,
            fill="x",
            padx=5
        )

        ctk.CTkLabel(
            self.cpu_card,
            text="CPU",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(15, 5))

        self.cpu_label = ctk.CTkLabel(
            self.cpu_card,
            text="0%",
            font=("Segoe UI", 30, "bold")
        )

        self.cpu_label.pack(pady=(0, 15))

        self.ram_card = ctk.CTkFrame(self.cards)

        self.ram_card.pack(
            side="left",
            expand=True,
            fill="x",
            padx=5
        )

        ctk.CTkLabel(
            self.ram_card,
            text="RAM",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(15, 5))

        self.ram_label = ctk.CTkLabel(
            self.ram_card,
            text="0%",
            font=("Segoe UI", 30, "bold")
        )

        self.ram_label.pack(pady=(0, 15))

        self.disk_card = ctk.CTkFrame(self.cards)

        self.disk_card.pack(
            side="left",
            expand=True,
            fill="x",
            padx=5
        )

        ctk.CTkLabel(
            self.disk_card,
            text="DISK",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(15, 5))

        self.disk_label = ctk.CTkLabel(
            self.disk_card,
            text="0%",
            font=("Segoe UI", 30, "bold")
        )

        self.disk_label.pack(pady=(0, 15))

        self.net_card = ctk.CTkFrame(self.cards)

        self.net_card.pack(
            side="left",
            expand=True,
            fill="x",
            padx=5
        )

        ctk.CTkLabel(
            self.net_card,
            text="NET",
            font=("Segoe UI", 18, "bold")
        ).pack(pady=(15, 5))

        self.net_label = ctk.CTkLabel(
            self.net_card,
            text="OK",
            font=("Segoe UI", 30, "bold")
        )

        self.net_label.pack(pady=(0, 15))

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

    def set_content(self, text):

        self.content.delete("1.0", "end")
        self.content.insert("1.0", text)
        def set_content(self, text):

    self.content.delete("1.0", "end")
    self.content.insert("1.0", text)
        def update_stats(self):

        cpu = psutil.cpu_percent()

        ram = psutil.virtual_memory().percent

        try:
            disk = psutil.disk_usage("C:\\").percent
        except:
            disk = 0

        self.cpu_label.configure(
            text=f"{cpu:.1f}%"
        )

        self.ram_label.configure(
            text=f"{ram:.1f}%"
        )

        self.disk_label.configure(
            text=f"{disk:.1f}%"
        )

        self.cpu_history.append(cpu)
        self.ram_history.append(ram)

        self.root.after(
            1000,
            self.update_stats
        )

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

            ax.set_ylim(
                0,
                100
            )

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

            update_graph()


if __name__ == "__main__":
    SystemMonitor()

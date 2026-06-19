import customtkinter as ctk
import psutil
import platform
import socket
import threading
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SystemMonitor:

    def __init__(self):

        self.root = ctk.CTk()
        self.root.title("Windows System Monitor Pro v6.0")
        self.root.geometry("1600x900")

        self.build_ui()

        self.root.after(1000, self.update_stats)

        self.show_summary()

        self.root.mainloop()

    def build_ui(self):

        # ===== SIDEBAR =====

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
            ("🌡 Температура GPU", self.show_gpu_temp),
            ("💽 Диски", self.show_disks),
            ("🌐 Сеть", self.show_network),
            ("⚙ Процессы", self.show_processes),
            ("🔥 Топ процессов", self.show_top_processes),
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

        # ===== MAIN =====

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

        # ===== CARDS =====

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

        # ===== CONTENT =====

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

    def show_summary(self):

        text = f"""
Компьютер: {socket.gethostname()}

Система:
{platform.system()} {platform.release()}

Процессор:
{platform.processor()}

Ядер:
{psutil.cpu_count(logical=False)}

Потоков:
{psutil.cpu_count()}

ОЗУ:
{round(psutil.virtual_memory().total / 1024**3, 1)} GB
"""

        self.set_content(text)

    def show_cpu(self):
        self.set_content("Загрузка CPU...\n\n(Часть 2)")

    def show_ram(self):
        self.set_content("Информация об ОЗУ...\n\n(Часть 2)")

    def show_gpu(self):
        self.set_content("Информация о GPU...\n\n(Часть 2)")

    def show_cpu_temp(self):
        self.set_content("Температура CPU...\n\n(Часть 3)")

    def show_gpu_temp(self):
        self.set_content("Температура GPU...\n\n(Часть 3)")

    def show_disks(self):
        self.set_content("Информация о дисках...\n\n(Часть 3)")

    def show_network(self):
        self.set_content("Информация о сети...\n\n(Часть 3)")

    def show_processes(self):
        self.set_content("Список процессов...\n\n(Часть 4)")

    def show_top_processes(self):
        self.set_content("ТОП процессов...\n\n(Часть 4)")

    def update_stats(self):

        cpu = psutil.cpu_percent()

        ram = psutil.virtual_memory().percent

        disk = psutil.disk_usage("C:\\").percent

        self.cpu_label.configure(text=f"{cpu:.1f}%")
        self.ram_label.configure(text=f"{ram:.1f}%")
        self.disk_label.configure(text=f"{disk:.1f}%")

        self.root.after(
            1000,
            self.update_stats
        )


SystemMonitor()

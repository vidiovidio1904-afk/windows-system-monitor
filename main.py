"""Windows System Monitor Pro.

Real-time system monitoring GUI: CPU, RAM, GPU, temperatures,
disks, network, processes and live graphs.

Run:
    python main.py
"""

from __future__ import annotations

import datetime
import platform
import socket
import webbrowser
from collections import deque

import customtkinter as ctk
import psutil
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

try:
    import GPUtil
except ImportError:  # GPUtil не обязателен — GPU-раздел просто покажет "нет данных"
    GPUtil = None

APP_NAME = "Windows System Monitor Pro"
UPDATE_INTERVAL_MS = 1000
HISTORY_LEN = 60

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ----------------------------------------------------------------------------
# Вспомогательные функции (тестируемые без GUI)
# ----------------------------------------------------------------------------

def format_bytes(num_bytes: float) -> str:
    """Человекочитаемый размер: байты -> KB/MB/GB/TB."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def format_uptime(seconds: float) -> str:
    """Аптайм системы в виде '1д 02:03:04'."""
    seconds = int(seconds)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{days}д {hours:02d}:{minutes:02d}:{secs:02d}"


def get_gpu_info() -> list[dict]:
    """Информация о видеокартах через GPUtil (пустой список, если недоступно)."""
    if GPUtil is None:
        return []
    try:
        gpus = GPUtil.getGPUs()
    except Exception:
        return []
    return [
        {
            "id": gpu.id,
            "name": gpu.name,
            "load": (gpu.load or 0) * 100,
            "memory_total": gpu.memoryTotal or 0,
            "memory_used": gpu.memoryUsed or 0,
            "temperature": gpu.temperature,
        }
        for gpu in gpus
    ]


def get_temperatures() -> list[tuple[str, float | None]]:
    """Температуры датчиков: [(имя, °C)]. Пытается psutil, затем WMI."""
    result: list[tuple[str, float | None]] = []
    try:
        sensors = psutil.sensors_temperatures()
    except (AttributeError, OSError):
        sensors = {}
    for name, entries in sensors.items():
        for entry in entries:
            label = entry.label or name
            result.append((label, entry.current))
    if result:
        return result
    # Windows: psutil обычно не даёт температуры, пробуем WMI
    try:
        import wmi  # type: ignore

        w = wmi.WMI(namespace="root\\wmi")
        for zone in w.MSAcpi_ThermalZoneTemperature():
            celsius = zone.CurrentTemperature / 10.0 - 273.15
            result.append(("Thermal Zone", round(celsius, 1)))
    except Exception:
        pass
    return result


def get_top_processes(limit: int = 20, by: str = "memory") -> list[tuple[str, float, str]]:
    """Топ процессов: by='memory' -> RAM MB, by='cpu' -> CPU %."""
    procs = []
    for proc in psutil.process_iter(["name", "username", "memory_info", "cpu_percent"]):
        try:
            info = proc.info
            name = info["name"] or "?"
            user = (info["username"] or "?").split("\\")[-1]
            if by == "memory":
                mem_mb = (info["memory_info"].rss / 1024**2) if info["memory_info"] else 0.0
                procs.append((name, mem_mb, user))
            else:
                procs.append((name, info["cpu_percent"] or 0.0, user))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    procs.sort(key=lambda p: p[1], reverse=True)
    return procs[:limit]


def build_html_report() -> str:
    """Полный HTML-отчёт о системе (сохраняется в report.html)."""
    mem = psutil.virtual_memory()
    boot = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = (datetime.datetime.now() - boot).total_seconds()
    gpus = get_gpu_info()
    gpu_rows = "".join(
        f"<tr><td>{g['name']}</td><td>{g['load']:.0f}%</td>"
        f"<td>{g['memory_used']:.0f} / {g['memory_total']:.0f} MB</td>"
        f"<td>{g['temperature'] or '—'} °C</td></tr>"
        for g in gpus
    ) or "<tr><td colspan='4'>Нет данных (GPUtil недоступен)</td></tr>"
    disk_rows = ""
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (OSError, PermissionError):
            continue
        disk_rows += (
            f"<tr><td>{part.device}</td><td>{format_bytes(usage.total)}</td>"
            f"<td>{format_bytes(usage.used)}</td><td>{usage.percent}%</td></tr>"
        )
    top_rows = "".join(
        f"<tr><td>{i}</td><td>{name}</td><td>{value:.1f}</td><td>{user}</td></tr>"
        for i, (name, value, user) in enumerate(get_top_processes(15), start=1)
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>{APP_NAME} — отчёт</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; background: #1e1e2e; color: #cdd6f4; }}
  h1 {{ color: #89b4fa; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0 32px; }}
  th, td {{ border: 1px solid #45475a; padding: 8px 12px; text-align: left; }}
  th {{ background: #313244; }}
  .muted {{ color: #6c7086; }}
</style>
</head>
<body>
<h1>{APP_NAME}</h1>
<p class="muted">Отчёт сформирован: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}</p>

<h2>Система</h2>
<table>
<tr><th>Компьютер</th><td>{socket.gethostname()}</td></tr>
<tr><th>ОС</th><td>{platform.system()} {platform.release()} ({platform.machine()})</td></tr>
<tr><th>Процессор</th><td>{platform.processor() or platform.machine()}</td></tr>
<tr><th>Ядер / потоков</th><td>{psutil.cpu_count(logical=False)} / {psutil.cpu_count()}</td></tr>
<tr><th>ОЗУ</th><td>{format_bytes(mem.total)} (занято {mem.percent}%)</td></tr>
<tr><th>Загружен с</th><td>{boot:%Y-%m-%d %H:%M:%S} (аптайм {format_uptime(uptime)})</td></tr>
</table>

<h2>Видеокарты</h2>
<table>
<tr><th>GPU</th><th>Загрузка</th><th>Память</th><th>Температура</th></tr>
{gpu_rows}
</table>

<h2>Диски</h2>
<table>
<tr><th>Диск</th><th>Всего</th><th>Занято</th><th>Загрузка</th></tr>
{disk_rows}
</table>

<h2>Топ-15 процессов по памяти (MB)</h2>
<table>
<tr><th>#</th><th>Имя</th><th>MB</th><th>Пользователь</th></tr>
{top_rows}
</table>
</body>
</html>"""


# ----------------------------------------------------------------------------
# GUI
# ----------------------------------------------------------------------------

class SystemMonitor:
    def __init__(self) -> None:
        self.root = ctk.CTk()
        self.root.title(APP_NAME)
        self.root.geometry("1280x800")
        self.root.minsize(1000, 640)

        self.cpu_history: deque[float] = deque([0.0] * HISTORY_LEN, maxlen=HISTORY_LEN)
        self.ram_history: deque[float] = deque([0.0] * HISTORY_LEN, maxlen=HISTORY_LEN)
        net = psutil.net_io_counters()
        self.net_sent_prev = net.bytes_sent
        self.net_recv_prev = net.bytes_recv
        self._graph_canvas = None
        self._graph_ax = None

        self.build_ui()
        self.show_summary()
        self.root.after(UPDATE_INTERVAL_MS, self.update_stats)
        self.root.mainloop()

    # ----- каркас интерфейса -------------------------------------------------

    def build_ui(self) -> None:
        self.sidebar = ctk.CTkFrame(self.root, width=260, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar, text="🖥 SYSTEM\nMONITOR",
            font=("Segoe UI", 22, "bold"), justify="center",
        ).pack(pady=(28, 20))

        menu = [
            ("📊 Сводка", self.show_summary),
            ("🖥 Процессор", self.show_cpu),
            ("🧠 Память", self.show_ram),
            ("🎮 Видеокарта", self.show_gpu),
            ("🌡 Температуры", self.show_temps),
            ("💽 Диски", self.show_disks),
            ("🌐 Сеть", self.show_network),
            ("⚙ Процессы", self.show_processes),
            ("🔥 Топ процессов", self.show_top_processes),
            ("📈 Графики", self.show_graphs),
        ]
        for text, command in menu:
            ctk.CTkButton(
                self.sidebar, text=text, height=38, command=command,
            ).pack(fill="x", padx=12, pady=3)

        ctk.CTkButton(
            self.sidebar, text="📄 HTML-отчёт", height=38,
            command=self.export_report,
        ).pack(fill="x", padx=12, pady=(3, 20))

        self.main = ctk.CTkFrame(self.root)
        self.main.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.header = ctk.CTkLabel(
            self.main, text="📊 Сводка", font=("Segoe UI", 30, "bold"),
        )
        self.header.pack(pady=(10, 5))

        # Карточки ключевых метрик
        self.cards = ctk.CTkFrame(self.main)
        self.cards.pack(fill="x", padx=10, pady=5)

        self.cpu_label = self._make_card("CPU")
        self.ram_label = self._make_card("RAM")
        self.disk_label = self._make_card("DISK")
        self.net_label = self._make_card("NET ↓/s")

        self.content = ctk.CTkTextbox(self.main, font=("Consolas", 14))
        self.content.pack(fill="both", expand=True, padx=10, pady=10)

    def _make_card(self, title: str) -> ctk.CTkLabel:
        card = ctk.CTkFrame(self.cards)
        card.pack(side="left", expand=True, fill="x", padx=5)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 16, "bold")).pack(pady=(12, 2))
        value = ctk.CTkLabel(card, text="—", font=("Segoe UI", 26, "bold"))
        value.pack(pady=(0, 12))
        return value

    def set_content(self, text: str) -> None:
        self._clear_graph()
        self.content.configure(state="normal")
        self.content.delete("1.0", "end")
        self.content.insert("1.0", text)
        self.content.configure(state="disabled")

    def _clear_graph(self) -> None:
        if self._graph_canvas is not None:
            self._graph_canvas.get_tk_widget().destroy()
            self._graph_canvas = None
            self._graph_ax = None

    # ----- разделы ------------------------------------------------------------

    def show_summary(self) -> None:
        self.header.configure(text="📊 Сводка")
        mem = psutil.virtual_memory()
        boot = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = (datetime.datetime.now() - boot).total_seconds()
        text = (
            f"Компьютер:      {socket.gethostname()}\n"
            f"Система:        {platform.system()} {platform.release()} ({platform.machine()})\n"
            f"Процессор:      {platform.processor() or platform.machine()}\n"
            f"Ядер/потоков:   {psutil.cpu_count(logical=False)} / {psutil.cpu_count()}\n"
            f"ОЗУ:            {format_bytes(mem.total)} (доступно {format_bytes(mem.available)})\n"
            f"Аптайм:         {format_uptime(uptime)}\n"
            f"Загружен с:     {boot:%Y-%m-%d %H:%M:%S}\n"
        )
        self.set_content(text)

    def show_cpu(self) -> None:
        self.header.configure(text="🖥 Процессор")
        per_core = psutil.cpu_percent(interval=0.3, percpu=True)
        freq = psutil.cpu_freq()
        freq_text = f"{freq.current:.0f} МГц" if freq else "н/д"
        per_core_text = "\n".join(
            f"  Ядро {i:>2}: {load:5.1f} %" for i, load in enumerate(per_core, start=1)
        )
        text = (
            f"Модель:         {platform.processor() or platform.machine()}\n"
            f"Ядер/потоков:   {psutil.cpu_count(logical=False)} / {psutil.cpu_count()}\n"
            f"Частота:        {freq_text}\n"
            f"Загрузка общая: {psutil.cpu_percent():.1f} %\n\n"
            f"Загрузка по ядрам:\n{per_core_text}\n"
        )
        self.set_content(text)

    def show_ram(self) -> None:
        self.header.configure(text="🧠 Память")
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        text = (
            f"Всего:          {format_bytes(mem.total)}\n"
            f"Используется:   {format_bytes(mem.used)} ({mem.percent:.1f} %)\n"
            f"Свободно:       {format_bytes(mem.available)}\n\n"
            f"Файл подкачки:  {format_bytes(swap.total)}\n"
            f"Занято в swap:  {format_bytes(swap.used)} ({swap.percent:.1f} %)\n"
        )
        self.set_content(text)

    def show_gpu(self) -> None:
        self.header.configure(text="🎮 Видеокарта")
        gpus = get_gpu_info()
        if not gpus:
            self.set_content(
                "Нет данных о GPU.\n\n"
                "GPUtil не обнаружил видеокарт или библиотека NVIDIA не установлена.\n"
                "GPU-мониторинг работает только с NVIDIA (NVML)."
            )
            return
        blocks = []
        for g in gpus:
            temp = f"{g['temperature']} °C" if g["temperature"] else "н/д"
            blocks.append(
                f"GPU #{g['id']}: {g['name']}\n"
                f"  Загрузка:     {g['load']:.1f} %\n"
                f"  Память:       {g['memory_used']:.0f} / {g['memory_total']:.0f} MB\n"
                f"  Температура:  {temp}\n"
            )
        self.set_content("\n".join(blocks))

    def show_temps(self) -> None:
        self.header.configure(text="🌡 Температуры")
        temps = get_temperatures()
        if not temps:
            self.set_content(
                "Датчики температуры недоступны.\n\n"
                "На большинстве Windows-конфигураций psutil не имеет доступа\n"
                "к сенсорам, а WMI отдаёт данные не на всех материнских платах.\n"
                "Попробуйте запуск от имени администратора."
            )
            return
        lines = [
            f"{name:<30} {temp:>6} °C" if temp is not None else f"{name:<30}    н/д"
            for name, temp in temps
        ]
        self.set_content("\n".join(lines))

    def show_disks(self) -> None:
        self.header.configure(text="💽 Диски")
        lines = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except (OSError, PermissionError):
                continue
            lines.append(
                f"{part.device:<12} {part.fstype or '?':<8}\n"
                f"  Всего: {format_bytes(usage.total):>10}   "
                f"Занято: {format_bytes(usage.used):>10}   "
                f"Свободно: {format_bytes(usage.free):>10}\n"
                f"  Загрузка: {usage.percent} %\n"
            )
        io = psutil.disk_io_counters()
        if io:
            lines.append(
                f"\nСуммарный I/O:\n"
                f"  Прочитано:  {format_bytes(io.read_bytes)} ({io.read_count} операций)\n"
                f"  Записано:   {format_bytes(io.write_bytes)} ({io.write_count} операций)\n"
            )
        self.set_content("\n".join(lines))

    def show_network(self) -> None:
        self.header.configure(text="🌐 Сеть")
        net = psutil.net_io_counters()
        lines = [
            f"Всего отправлено:  {format_bytes(net.bytes_sent)}",
            f"Всего получено:    {format_bytes(net.bytes_recv)}",
            "",
            "Интерфейсы:",
        ]
        for name, addrs in psutil.net_if_addrs().items():
            ip = next((a.address for a in addrs if a.family.name == "AF_INET"), None)
            lines.append(f"  {name:<35} {ip or 'нет IPv4'}")
        try:
            conns = len(psutil.net_connections(kind="inet"))
        except (psutil.AccessDenied, OSError):
            conns = None
        if conns is not None:
            lines += ["", f"Активных соединений: {conns}"]
        else:
            lines += ["", "Активные соединения: нужны права администратора"]
        self.set_content("\n".join(lines))

    def show_processes(self) -> None:
        self.header.configure(text="⚙ Процессы")
        lines = [f"{'PID':>7}  {'Имя':<32} Пользователь", "-" * 60]
        for proc in psutil.process_iter(["pid", "name", "username"]):
            try:
                info = proc.info
                user = (info["username"] or "?").split("\\")[-1]
                lines.append(f"{info['pid']:>7}  {info['name'] or '?':<32} {user}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        self.set_content("\n".join(lines))

    def show_top_processes(self) -> None:
        self.header.configure(text="🔥 Топ процессов по памяти")
        lines = [f"{'#':>3}  {'Имя':<32} {'RAM, MB':>10}  Пользователь", "-" * 70]
        for i, (name, mem_mb, user) in enumerate(get_top_processes(25), start=1):
            lines.append(f"{i:>3}  {name:<32} {mem_mb:>10.1f}  {user}")
        self.set_content("\n".join(lines))

    def show_graphs(self) -> None:
        self.header.configure(text="📈 Графики в реальном времени")
        self._clear_graph()
        self.content.configure(state="normal")
        self.content.delete("1.0", "end")
        self.content.configure(state="disabled")

        figure = Figure(figsize=(9, 4.5), dpi=100)
        self._graph_ax = figure.add_subplot(111)
        self._graph_canvas = FigureCanvasTkAgg(figure, master=self.content)
        self._graph_canvas.get_tk_widget().pack(fill="both", expand=True)
        self._draw_graph()

    def _draw_graph(self) -> None:
        if self._graph_canvas is None:
            return
        ax = self._graph_ax
        ax.clear()
        ax.plot(list(self.cpu_history), label="CPU %", color="#89b4fa")
        ax.plot(list(self.ram_history), label="RAM %", color="#a6e3a1")
        ax.set_ylim(0, 100)
        ax.set_xlim(0, HISTORY_LEN - 1)
        ax.set_title("Real-time monitoring (последние 60 секунд)")
        ax.set_xlabel("секунды назад")
        ax.legend(loc="upper right")
        self._graph_canvas.draw()
        self.root.after(UPDATE_INTERVAL_MS, self._draw_graph)

    # ----- действия -----------------------------------------------------------

    def export_report(self) -> None:
        path = "report.html"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(build_html_report())
        self.header.configure(text=f"📄 Отчёт сохранён: {path}")
        try:
            webbrowser.open(path)
        except OSError:
            pass

    # ----- периодическое обновление -------------------------------------------

    def update_stats(self) -> None:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        try:
            disk = psutil.disk_usage("C:\\").percent
        except OSError:
            disk = 0.0

        net = psutil.net_io_counters()
        recv_speed = (net.bytes_recv - self.net_recv_prev) / (UPDATE_INTERVAL_MS / 1000)
        self.net_sent_prev, self.net_recv_prev = net.bytes_sent, net.bytes_recv

        self.cpu_label.configure(text=f"{cpu:.1f}%")
        self.ram_label.configure(text=f"{ram:.1f}%")
        self.disk_label.configure(text=f"{disk:.1f}%")
        self.net_label.configure(text=f"{format_bytes(recv_speed)}/s")

        self.cpu_history.append(cpu)
        self.ram_history.append(ram)

        self.root.after(UPDATE_INTERVAL_MS, self.update_stats)


if __name__ == "__main__":
    SystemMonitor()

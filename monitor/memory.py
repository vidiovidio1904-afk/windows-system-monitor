def show_ram(self):
    ram = psutil.virtual_memory()

    text = f"""
Всего:
{ram.total / 1024**3:.1f} GB

Используется:
{ram.used / 1024**3:.1f} GB

Свободно:
{ram.available / 1024**3:.1f} GB

Загрузка:
{ram.percent} %
"""
    self.set_content(text)

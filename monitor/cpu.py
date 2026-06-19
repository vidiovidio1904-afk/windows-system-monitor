def show_cpu(self):
    text = f"""
CPU: {platform.processor()}

Загрузка:
{psutil.cpu_percent()} %

Ядер:
{psutil.cpu_count(logical=False)}

Потоков:
{psutil.cpu_count()}
"""
    self.set_content(text)

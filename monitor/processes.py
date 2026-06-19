def show_processes(self):

    text = ""

    for proc in psutil.process_iter(['pid', 'name']):

        try:
            text += f"{proc.info['pid']} | {proc.info['name']}\n"
        except:
            pass

    self.set_content(text)

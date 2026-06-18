import tkinter as tk

root = tk.Tk()

root.title("Windows System Monitor")
root.geometry("600x400")

label = tk.Label(
    root,
    text="Windows System Monitor",
    font=("Arial", 20)
)

label.pack(pady=50)

root.mainloop()

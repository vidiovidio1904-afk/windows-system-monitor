import psutil

def get_cpu_info():
    freq = psutil.cpu_freq()

    return {
        "usage": psutil.cpu_percent(),
        "cores": psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(),
        "frequency": round(freq.current)
    }

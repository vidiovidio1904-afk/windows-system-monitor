import psutil

def get_memory_info():

    mem = psutil.virtual_memory()

    return {
        "total": round(mem.total / 1024**3, 2),
        "used": round(mem.used / 1024**3, 2),
        "free": round(mem.available / 1024**3, 2),
        "percent": mem.percent
    }

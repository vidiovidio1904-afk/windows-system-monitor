import psutil

def get_disks():

    result = []

    for part in psutil.disk_partitions():

        try:

            usage = psutil.disk_usage(part.mountpoint)

            result.append({
                "device": part.device,
                "total": round(usage.total / 1024**3, 1),
                "free": round(usage.free / 1024**3, 1),
                "used": usage.percent
            })

        except:
            pass

    return result

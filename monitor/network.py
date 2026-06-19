import psutil

def get_network_info():

    net = psutil.net_io_counters()

    return {
        "sent": round(net.bytes_sent / 1024**2, 2),
        "recv": round(net.bytes_recv / 1024**2, 2)
    }

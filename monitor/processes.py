import psutil

def get_top_processes(limit=20):

    processes = []

    for proc in psutil.process_iter(
        ['pid', 'name', 'memory_percent']
    ):

        try:
            processes.append(proc.info)
        except:
            pass

    return sorted(
        processes,
        key=lambda x: x['memory_percent'],
        reverse=True
    )[:limit]

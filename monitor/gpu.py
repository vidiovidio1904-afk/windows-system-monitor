import GPUtil

def get_gpu_info():

    gpus = GPUtil.getGPUs()

    if not gpus:
        return None

    gpu = gpus[0]

    return {
        "name": gpu.name,
        "load": round(gpu.load * 100),
        "temperature": gpu.temperature
    }

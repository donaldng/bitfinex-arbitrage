import config

def get_host():
    return config.host if config.host else None

def get_port():
    return config.port if config.port else None
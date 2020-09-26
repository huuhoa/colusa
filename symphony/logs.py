from symphony import colors


def error(msg, *args, **kwargs):
    print(colors.red("[ERROR]"), msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
    print(colors.yellow("[WARN]"), msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    print("[INFO]", msg, *args, **kwargs)

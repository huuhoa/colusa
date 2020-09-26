from colusa import colors


def error(msg, *args, **kwargs):
    print(colors.red("[ERROR]"), msg, *args, **kwargs)


def warn(msg, *args, **kwargs):
    print(colors.yellow("[WARN]"), msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    print(colors.green("[INFO]"), msg, *args, **kwargs)

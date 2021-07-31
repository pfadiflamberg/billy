import os


def getenv(name):
    value = os.getenv(name)
    if len(value) == 0:
        raise Exception("missing environment variable: " + name)
    return value

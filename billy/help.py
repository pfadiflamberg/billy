import os


def getenv(name):
    value = os.getenv(name)
    if not value or len(value) == 0:
        raise Exception("missing environment variable: " + name)
    return value

verbs = {}


def verb(func):
    verbs[func.__name__] = func
    return func

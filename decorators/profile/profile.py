import time
from functools import wraps
import types


def timer(func: types.FunctionType):
    @wraps(func)
    def wrapped(*args, **kwargs):
        print(f"'{func.__qualname__}' started")
        start = time.time()
        result = func(*args, **kwargs)
        run_time = time.time() - start
        print(f"'{func.__qualname__}' finished in {run_time}s")
        return result

    return wrapped


def profile(obj: object):
    if isinstance(obj, types.FunctionType):
        return timer(obj)
    for attr_name in dir(obj):
        attr = getattr(obj, attr_name)
        if isinstance(attr, types.FunctionType):
            setattr(obj, attr_name, timer(attr))
    return obj
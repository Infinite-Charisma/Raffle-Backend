import time
from json import JSONDecodeError
from functools import wraps
import inspect


def retriable(count=5, exceptions=(JSONDecodeError, ), delay=0.5):
    def wrapper(f):
        if inspect.iscoroutinefunction(f):
            @wraps(f)
            async def decorator_async(*args, **kwargs):
                try_count = 0
                while True:
                    try:
                        try_count += 1
                        return await f(*args, **kwargs)
                    except exceptions as e:
                        if try_count >= count:
                            raise Exception(f"Failed after {try_count} tries") from e
                        time.sleep(delay)
                    except Exception as e:
                        raise Exception(f"Failed with unexpected exception {e}") from e
            return decorator_async

        @wraps(f)
        def decorator(*args, **kwargs):
            try_count = 0
            while True:
                try:
                    try_count += 1
                    return f(*args, **kwargs)
                except exceptions as e:
                    if try_count >= count:
                        raise Exception(f"Failed after {try_count} tries") from e
                    time.sleep(delay)
        return decorator
    return wrapper

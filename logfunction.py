import logging
from functools import wraps


def log_func(filename):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Configure logger
            if not hasattr(wrapper, "logger"):
                wrapper.logger = logging.getLogger(__name__)
                handler = logging.FileHandler(filename)
                formatter = logging.Formatter("%(asctime)s - %(name)s: %(message)s")
                handler.setFormatter(formatter)
                wrapper.logger.addHandler(handler)
                wrapper.logger.setLevel(logging.INFO)

            # Log function name and arguments
            log_message = f"Function: {func.__name__}, Arguments: {args}, {kwargs}"
            wrapper.logger.info(log_message)

            # Call the original function and return the result
            return func(*args, **kwargs)

        return wrapper

    return decorator

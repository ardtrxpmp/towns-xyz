import functools
from loguru import logger
from core.utils.helpers import sleeping
from data.config import CONFIG_FILE


def retry(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(CONFIG_FILE["settings"]["general"]["max_retries"]):
            try:
                res = func(*args, **kwargs)
                return res
            except Exception as e:
                logger.warning(f"{func.__name__} - exception: {str(e)}")
                if "insufficient funds" in str(e):
                    return
                sleeping(mode=3)
        else:
            return

    return wrapper

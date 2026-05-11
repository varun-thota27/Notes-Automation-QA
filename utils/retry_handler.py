import time
from functools import wraps

from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    TimeoutException
)


def retry_on_failure(max_retries=3, delay=2):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            last_exception = None

            for attempt in range(max_retries):

                try:
                    return func(*args, **kwargs)

                except (
                    StaleElementReferenceException,
                    ElementClickInterceptedException,
                    TimeoutException
                ) as e:

                    last_exception = e

                    print(
                        f"[Retry Handler] "
                        f"Attempt {attempt + 1} failed"
                    )

                    time.sleep(delay)

            raise last_exception

        return wrapper

    return decorator
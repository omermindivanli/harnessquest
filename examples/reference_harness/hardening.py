"""Level 19 reference: never let one slow call hang the harness."""

import concurrent.futures


def run_with_timeout(func, seconds):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(func)
    try:
        return future.result(timeout=seconds)
    except concurrent.futures.TimeoutError:
        raise TimeoutError(f"call exceeded {seconds}s") from None
    finally:
        executor.shutdown(wait=False)

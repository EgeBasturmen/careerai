import time

from fastapi import Request

from src.core.logging.logger import logger


async def request_logging_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    logger.info(
        f"{request.method} {request.url.path} "
        f"{response.status_code} "
        f"{duration_ms:.2f}ms"
    )

    return response
from fastapi import Request
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from src.core.logging.logger import logger


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    logger.warning(
        f"HTTP error: {exc.status_code} - {exc.detail}"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail,
                "status_code": exc.status_code,
            }
        },
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled server error"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "status_code": 500,
            }
        },
    )
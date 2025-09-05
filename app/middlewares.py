from fastapi import Request
import structlog

logger = structlog.get_logger()

async def log_requests(request: Request, call_next):
    logger.info("request.start", method=request.method, path=request.url.path)
    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception("request.error", error=str(e))
        raise
    logger.info("request.end", status_code=response.status_code)
    return response

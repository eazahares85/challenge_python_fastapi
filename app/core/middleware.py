import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time

logger = logging.getLogger(__name__)

class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware para manejo centralizado de excepciones"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Agregar header de tiempo de procesamiento
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except HTTPException as e:
            logger.warning(f"HTTP Exception: {e.detail} - Path: {request.url.path}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail, "error": "HTTP_ERROR"}
            )
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)} - Path: {request.url.path}")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error": "INTERNAL_ERROR"
                }
            )

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log del request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Log del response
        logger.info(
            f"Response: {response.status_code} - "
            f"Time: {process_time:.4f}s - "
            f"Path: {request.url.path}"
        )
        
        return response

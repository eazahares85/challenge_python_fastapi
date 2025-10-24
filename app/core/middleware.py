import logging
import sys
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time

# Configurar logging para mostrar en consola
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

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
    """Middleware para logging detallado de requests con tiempo de respuesta"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Información del request
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log del request entrante
        print(f"\n[INCOMING] [{timestamp}] REQUEST INCOMING")
        print(f"   Method: {request.method}")
        print(f"   Path: {request.url.path}")
        print(f"   Query: {request.url.query}")
        print(f"   Client IP: {client_ip}")
        print(f"   User-Agent: {user_agent[:50]}...")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Agregar header de tiempo de procesamiento
            response.headers["X-Process-Time"] = str(round(process_time, 4))
            
            # Log del response
            status_emoji = "[OK]" if response.status_code < 400 else "[ERROR]"
            print(f"\n{status_emoji} [{timestamp}] RESPONSE SENT")
            print(f"   Status: {response.status_code}")
            print(f"   Time: {process_time:.4f}s")
            print(f"   Path: {request.url.path}")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            
            # Log en consola con formato especial para tiempo de respuesta
            print(f"[TIME] Response Time: {process_time:.4f}s for {request.method} {request.url.path}")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            print(f"\n[ERROR] [{timestamp}] ERROR OCCURRED")
            print(f"   Error: {str(e)}")
            print(f"   Time: {process_time:.4f}s")
            print(f"   Path: {request.url.path}")
            raise

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware para métricas de rendimiento y estadísticas"""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.total_time = 0.0
        self.slow_requests = []
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        self.request_count += 1
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        self.total_time += process_time
        
        # Registrar requests lentos (>1 segundo)
        if process_time > 1.0:
            self.slow_requests.append({
                "path": request.url.path,
                "method": request.method,
                "time": process_time,
                "timestamp": datetime.now().isoformat()
            })
        
        # Agregar estadísticas al header
        avg_time = self.total_time / self.request_count
        response.headers["X-Total-Requests"] = str(self.request_count)
        response.headers["X-Average-Time"] = str(round(avg_time, 4))
        response.headers["X-Slow-Requests-Count"] = str(len(self.slow_requests))
        
        return response
    
    def get_stats(self):
        """Obtener estadísticas de rendimiento"""
        return {
            "total_requests": self.request_count,
            "total_time": round(self.total_time, 4),
            "average_time": round(self.total_time / self.request_count, 4) if self.request_count > 0 else 0,
            "slow_requests_count": len(self.slow_requests),
            "slow_requests": self.slow_requests[-10:]  # Últimos 10 requests lentos
        }

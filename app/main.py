from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.core.middleware import ExceptionHandlingMiddleware, LoggingMiddleware, PerformanceMiddleware
from app.api.endpoints import auth, users, posts, comments, tags, items

# Crear tablas
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar middlewares
app.add_middleware(ExceptionHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(PerformanceMiddleware)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(posts.router, prefix=f"{settings.API_V1_STR}/posts", tags=["posts"])
app.include_router(comments.router, prefix=f"{settings.API_V1_STR}/comments", tags=["comments"])
app.include_router(tags.router, prefix=f"{settings.API_V1_STR}/tags", tags=["tags"])
app.include_router(items.router, prefix=f"{settings.API_V1_STR}/items", tags=["items"])

@app.on_event("startup")
async def startup_event():
    await create_tables()

@app.get("/stats")
async def get_performance_stats():
    """Obtener estadísticas de rendimiento de la API"""
    # Obtener el middleware de rendimiento
    performance_middleware = None
    for middleware in app.user_middleware:
        if hasattr(middleware, 'cls') and middleware.cls == PerformanceMiddleware:
            performance_middleware = middleware.cls(app)
            break
    
    if performance_middleware:
        return performance_middleware.get_stats()
    else:
        return {"message": "Performance middleware not found"}

@app.get("/")
async def root():
    return {"message": "Bienvenido a mi API RESTful con FastAPI, Pydantic v2 y SQLAlchemy 2.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
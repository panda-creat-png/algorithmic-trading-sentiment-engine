from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import init_db, check_db_connection
from app.core.redis import check_redis_connection, close_redis
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} backend in {settings.ENVIRONMENT} mode...")
    
    # Initialize DB tables
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Log connection states
    db_status = await check_db_connection()
    logger.info(f"Database status: {db_status}")
    
    redis_status = await check_redis_connection()
    logger.info(f"Redis status: {redis_status}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down QuantMind AI backend...")
    await close_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Institutional-grade AI Algorithmic Trading & Sentiment Engine API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "online",
        "docs": f"{settings.API_V1_STR}/docs",
    }


@app.get("/healthz", tags=["Health"])
async def healthz():
    db_status = await check_db_connection()
    redis_status = await check_redis_connection()
    return {
        "status": "healthy" if db_status.get("status") == "connected" else "degraded",
        "database": db_status.get("status"),
        "redis": redis_status.get("status"),
    }


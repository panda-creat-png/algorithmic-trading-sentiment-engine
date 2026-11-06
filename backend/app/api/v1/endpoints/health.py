from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings
from app.core.database import check_db_connection
from app.core.redis import check_redis_connection
from app.schemas.health import HealthResponse, ServiceStatus

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="System Health & Diagnostic Status")
async def get_health_status():
    """Returns real-time health checks for DB, Redis, and backend services."""
    db_status_dict = await check_db_connection()
    redis_status_dict = await check_redis_connection()

    db_healthy = db_status_dict.get("status") == "connected"
    redis_healthy = redis_status_dict.get("status") in ("connected", "fallback_active")

    overall_status = "ok" if (db_healthy and redis_healthy) else "degraded"
    if not db_healthy and not redis_healthy:
        overall_status = "critical"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        database=ServiceStatus(**db_status_dict),
        redis=ServiceStatus(**redis_status_dict),
        meta={
            "app_name": settings.PROJECT_NAME,
            "debug": settings.DEBUG,
            "active_cors_origins": len(settings.CORS_ORIGINS),
        }
    )


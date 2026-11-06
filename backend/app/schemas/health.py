from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ServiceStatus(BaseModel):
    status: str
    latency_ms: Optional[float] = None
    database_type: Optional[str] = None
    backend: Optional[str] = None
    note: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall system health status: ok | degraded | critical")
    timestamp: str = Field(..., description="Current UTC timestamp")
    version: str = Field(default="1.0.0", description="API version")
    environment: str = Field(..., description="Application environment")
    database: ServiceStatus
    redis: ServiceStatus
    meta: Dict[str, Any] = Field(default_factory=dict)


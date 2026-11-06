from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class NewsArticleBase(BaseModel):
    title: str = Field(..., max_length=512)
    url: Optional[str] = None
    source: str = Field(..., max_length=64)
    summary: Optional[str] = None
    content: Optional[str] = None
    published_at: datetime
    author: Optional[str] = None
    raw_metadata: Optional[Dict[str, Any]] = None


class NewsArticleCreate(NewsArticleBase):
    pass


class NewsArticleResponse(NewsArticleBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


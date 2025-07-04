from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from typing import List

class APIKey(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    key: str = Field(index=True, nullable=False, unique=True)
    owner : str
    created_at : datetime = Field(default_factory=lambda : datetime.now(timezone.utc))

class APIKeyCreate(SQLModel):
    owner : str

class ResponseLog(SQLModel, table = True):
    id : int | None = Field(default=None, primary_key=True)
    api_key : str = Field(index=True, nullable=False)
    latency : float
    status_code : int
    url : str
    timestamp : datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Metrics(SQLModel):
    total_requests : int
    avg_latency : float
    recent_rate_limited_request_count : int
    recent_codes : List[int]
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone

class APIKey(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    key: str = Field(index=True, nullable=False, unique=True)
    owner : str
    created_at : datetime = Field(default_factory=lambda : datetime.now(timezone.utc))

class APIKeyCreate(SQLModel):
    owner : str
"""
Campaigns Models — Python Dataclasses
----------------------------------------
Plain data containers mirroring the `campaigns` table.
DB schema is defined in schema.sql.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List


@dataclass
class Campaign:
    id: int
    user_id: int
    title: str
    status: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = None
    budget: Optional[Decimal] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    metadata: Optional[dict] = None

    @classmethod
    def from_row(cls, row: dict) -> "Campaign":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            description=row.get("description"),
            status=row["status"],
            budget=row.get("budget"),
            start_date=row.get("start_date"),
            end_date=row.get("end_date"),
            tags=row.get("tags") or [],
            metadata=row.get("metadata"),
            is_deleted=row["is_deleted"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "user_id":     self.user_id,
            "title":       self.title,
            "description": self.description,
            "status":      self.status,
            "budget":      str(self.budget) if self.budget else None,
            "start_date":  self.start_date.isoformat() if self.start_date else None,
            "end_date":    self.end_date.isoformat() if self.end_date else None,
            "tags":        self.tags,
            "metadata":    self.metadata or {},
            "created_at":  self.created_at.isoformat() if self.created_at else None,
            "updated_at":  self.updated_at.isoformat() if self.updated_at else None,
        }

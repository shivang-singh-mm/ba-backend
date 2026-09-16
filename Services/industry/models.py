"""
Industry Models — Python Dataclasses
---------------------------------------
Data container mirroring the industries table.
DB schema is defined in schema.sql — not here.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Industry:
    id: int
    name: str
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "Industry":
        """Construct an Industry from a psycopg2 RealDictRow."""
        return cls(
            id=row["id"],
            name=row["name"],
            user_id=row.get("user_id"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        """Serialise to a public-facing dict."""
        return {
            "id":         self.id,
            "name":       self.name,
            "user_id":    self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

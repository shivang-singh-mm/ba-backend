"""
User Models — Python Dataclasses
----------------------------------
These are plain Python data containers that mirror the `users` table.
DB schema is defined in schema.sql — not here.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    phone: Optional[str] = None
    experiences: list["UserExperience"] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: dict, experiences: list = None) -> "User":
        """Construct a User from a psycopg2 RealDictRow."""
        return cls(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            phone=row.get("phone"),
            role=row["role"],
            is_active=row["is_active"],
            is_deleted=row["is_deleted"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            experiences=experiences or [],
        )

    def to_dict(self) -> dict:
        """Serialise to a safe public-facing dict."""
        return {
            "id":          self.id,
            "name":        self.name,
            "email":       self.email,
            "phone":       self.phone,
            "role":        self.role,
            "is_active":   self.is_active,
            "experiences": [e.to_dict() for e in self.experiences],
            "created_at":  self.created_at.isoformat() if self.created_at else None,
            "updated_at":  self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class UserExperience:
    id: int
    user_id: int
    brand_name: str
    role_name: str
    duration: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "UserExperience":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            brand_name=row["brand_name"],
            role_name=row["role_name"],
            duration=row.get("duration"),
            description=row.get("description"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "user_id":     self.user_id,
            "brand_name":  self.brand_name,
            "role_name":   self.role_name,
            "duration":    self.duration,
            "description": self.description,
        }


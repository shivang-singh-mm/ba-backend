"""
Brand Models — Python Dataclasses
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class BrandProfile:
    id: int
    user_id: int
    brand_name: str
    brand_description: Optional[str]
    brand_logo_url: Optional[str]
    brand_website: Optional[str]
    city_id: Optional[int]
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    industries: list[dict] = field(default_factory=list)
    locations: list[dict] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: dict, industries: list = None, locations: list = None) -> "BrandProfile":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            brand_name=row["brand_name"],
            brand_description=row.get("brand_description"),
            brand_logo_url=row.get("brand_logo_url"),
            brand_website=row.get("brand_website"),
            city_id=row.get("city_id"),
            is_verified=row["is_verified"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            industries=industries or [],
            locations=locations or [],
        )

    def to_dict(self) -> dict:
        return {
            "id":                self.id,
            "user_id":           self.user_id,
            "brand_name":        self.brand_name,
            "brand_description": self.brand_description,
            "brand_logo_url":    self.brand_logo_url,
            "brand_website":     self.brand_website,
            "city_id":           self.city_id,
            "is_verified":       self.is_verified,
            "is_active":         self.is_active,
            "industries":        self.industries,
            "locations":         self.locations,
            "created_at":        self.created_at.isoformat() if self.created_at else None,
            "updated_at":        self.updated_at.isoformat() if self.updated_at else None,
        }

"""
Provider Models — Python Dataclasses
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from .enum import PROVIDER_TYPE, PROFICIENCY, DOCUMENT_TYPE


@dataclass
class ProviderProfile:
    id: int
    user_id: int
    provider_type: str
    description: Optional[str]
    current_occupation: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    profile_image_url: Optional[str]
    city_id: Optional[int]
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    industries: list[dict] = field(default_factory=list)
    skills: list[dict] = field(default_factory=list)
    languages: list[dict] = field(default_factory=list)
    documents: list[dict] = field(default_factory=list)
    experiences: list[dict] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: dict, industries: list = None, skills: list = None, languages: list = None, documents: list = None, experiences: list = None) -> "ProviderProfile":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            provider_type=PROVIDER_TYPE.get(row["provider_type"], "individual"),
            description=row.get("description"),
            current_occupation=row.get("current_occupation"),
            date_of_birth=row.get("date_of_birth"),
            gender=row.get("gender"),
            profile_image_url=row.get("profile_image_url"),
            city_id=row.get("city_id"),
            is_verified=row["is_verified"],
            is_active=row["is_active"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            industries=industries or [],
            skills=skills or [],
            languages=languages or [],
            documents=documents or [],
            experiences=experiences or [],
        )

    def to_dict(self) -> dict:
        return {
            "id":                 self.id,
            "user_id":            self.user_id,
            "provider_type":      self.provider_type,
            "description":        self.description,
            "current_occupation": self.current_occupation,
            "date_of_birth":      self.date_of_birth.isoformat() if self.date_of_birth else None,
            "gender":             self.gender,
            "profile_image_url":  self.profile_image_url,
            "city_id":            self.city_id,
            "is_verified":        self.is_verified,
            "is_active":          self.is_active,
            "industries":         self.industries,
            "skills":             self.skills,
            "languages":          self.languages,
            "documents":          self.documents,
            "experiences":        self.experiences,
            "created_at":         self.created_at.isoformat() if self.created_at else None,
            "updated_at":         self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class ProviderExperience:
    id: int
    provider_id: int
    brand_name: str
    role_name: str
    duration: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "ProviderExperience":
        return cls(
            id=row["id"],
            provider_id=row["provider_id"],
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
            "provider_id": self.provider_id,
            "brand_name":  self.brand_name,
            "role_name":   self.role_name,
            "duration":    self.duration,
            "description": self.description,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
            "updated_at":  self.updated_at.isoformat() if self.updated_at else None,
        }

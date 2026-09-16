"""
Location Models — Python Dataclasses
---------------------------------------
Data containers mirroring the countries, states, and cities tables.
DB schema is defined in schema.sql — not here.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Country:
    id: int
    name: str
    country_code: str
    phone_code: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "Country":
        """Construct a Country from a psycopg2 RealDictRow."""
        return cls(
            id=row["id"],
            name=row["name"],
            country_code=row["country_code"],
            phone_code=row["phone_code"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        """Serialise to a public-facing dict."""
        return {
            "id":           self.id,
            "name":         self.name,
            "country_code": self.country_code,
            "phone_code":   self.phone_code,
            "created_at":   self.created_at.isoformat() if self.created_at else None,
            "updated_at":   self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class State:
    id: int
    name: str
    country_id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "State":
        """Construct a State from a psycopg2 RealDictRow."""
        return cls(
            id=row["id"],
            name=row["name"],
            country_id=row["country_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        """Serialise to a public-facing dict."""
        return {
            "id":         self.id,
            "name":       self.name,
            "country_id": self.country_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class City:
    id: int
    name: str
    state_id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "City":
        """Construct a City from a psycopg2 RealDictRow."""
        return cls(
            id=row["id"],
            name=row["name"],
            state_id=row["state_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        """Serialise to a public-facing dict."""
        return {
            "id":         self.id,
            "name":       self.name,
            "state_id":   self.state_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

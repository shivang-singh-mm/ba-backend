"""
Campaigns Models — Python Dataclasses
----------------------------------------
Plain data containers mirroring the `campaigns` and `campaign_props` tables.
DB schema is defined in schema.sql.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional

from .enum import STATUS


@dataclass
class Campaign:
    id: int
    user_id: int
    title: str
    status: str          # human-readable string; DB stores integer
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = None
    total_hours: Optional[Decimal] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    date: Optional[date] = None
    target: Optional[str] = None
    locality: Optional[str] = None

    @classmethod
    def from_row(cls, row: dict) -> "Campaign":
        """Construct a Campaign from a psycopg2 RealDictRow."""
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            description=row.get("description"),
            total_hours=row.get("total_hours"),
            start_time=row.get("start_time"),
            end_time=row.get("end_time"),
            date=row.get("date"),
            target=row.get("target"),
            locality=row.get("locality"),
            status=STATUS.get(row["status"], "draft"),
            is_deleted=row["is_deleted"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        """Serialise to a public-facing dict."""
        return {
            "id":          self.id,
            "user_id":     self.user_id,
            "title":       self.title,
            "description": self.description,
            "total_hours": str(self.total_hours) if self.total_hours is not None else None,
            "start_time":  self.start_time.isoformat() if self.start_time else None,
            "end_time":    self.end_time.isoformat() if self.end_time else None,
            "date":        self.date.isoformat() if self.date else None,
            "target":      self.target,
            "locality":    self.locality,
            "status":      self.status,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
            "updated_at":  self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class CampaignProps:
    id: int
    campaign_id: int
    stalls: int
    tables: int
    chairs: int
    led: int
    banners: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "CampaignProps":
        """Construct a CampaignProps from a psycopg2 RealDictRow."""
        return cls(
            id=row["id"],
            campaign_id=row["campaign_id"],
            stalls=row["stalls"],
            tables=row["tables"],
            chairs=row["chairs"],
            led=row["led"],
            banners=row["banners"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        """Serialise to a public-facing dict."""
        return {
            "id":          self.id,
            "campaign_id": self.campaign_id,
            "stalls":      self.stalls,
            "tables":      self.tables,
            "chairs":      self.chairs,
            "led":         self.led,
            "banners":     self.banners,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
            "updated_at":  self.updated_at.isoformat() if self.updated_at else None,
        }

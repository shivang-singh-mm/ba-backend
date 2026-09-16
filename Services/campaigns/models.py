"""
Campaigns Models — Python Dataclasses
----------------------------------------
Plain data containers mirroring the campaigns module tables.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List, Dict, Any

from .enum import STATUS, PROFICIENCY


@dataclass
class CampaignProduct:
    id: int
    campaign_id: int
    product_name: str
    product_description: Optional[str] = None
    product_url: Optional[str] = None
    offer_description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row: dict) -> "CampaignProduct":
        return cls(
            id=row["id"],
            campaign_id=row["campaign_id"],
            product_name=row["product_name"],
            product_description=row.get("product_description"),
            product_url=row.get("product_url"),
            offer_description=row.get("offer_description"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id":                  self.id,
            "campaign_id":         self.campaign_id,
            "product_name":        self.product_name,
            "product_description": self.product_description,
            "product_url":         self.product_url,
            "offer_description":   self.offer_description,
            "created_at":          self.created_at.isoformat() if self.created_at else None,
            "updated_at":          self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class CampaignVenue:
    id: int
    campaign_id: int
    venue_type_id: Optional[int] = None
    venue_type_name: Optional[str] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row: dict) -> "CampaignVenue":
        return cls(
            id=row["id"],
            campaign_id=row["campaign_id"],
            venue_type_id=row.get("venue_type_id"),
            venue_type_name=row.get("venue_type_name"),
            venue_name=row.get("venue_name"),
            venue_address=row.get("venue_address"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id":              self.id,
            "campaign_id":     self.campaign_id,
            "venue_type_id":   self.venue_type_id,
            "venue_type_name": self.venue_type_name,
            "venue_name":      self.venue_name,
            "venue_address":   self.venue_address,
            "created_at":      self.created_at.isoformat() if self.created_at else None,
            "updated_at":      self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class CampaignAudience:
    id: int
    campaign_id: int
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: Optional[str] = None
    income_min: Optional[Decimal] = None
    income_max: Optional[Decimal] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    life_stage: Optional[str] = None
    geography: Optional[str] = None
    origin: Optional[str] = None
    interests: Optional[str] = None
    lifestyle: Optional[str] = None
    purchase_behavior: Optional[str] = None
    audience_size: Optional[int] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row: dict) -> "CampaignAudience":
        return cls(
            id=row["id"],
            campaign_id=row["campaign_id"],
            min_age=row.get("min_age"),
            max_age=row.get("max_age"),
            gender=row.get("gender"),
            income_min=row.get("income_min"),
            income_max=row.get("income_max"),
            occupation=row.get("occupation"),
            education=row.get("education"),
            life_stage=row.get("life_stage"),
            geography=row.get("geography"),
            origin=row.get("origin"),
            interests=row.get("interests"),
            lifestyle=row.get("lifestyle"),
            purchase_behavior=row.get("purchase_behavior"),
            audience_size=row.get("audience_size"),
            description=row.get("description"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id":                self.id,
            "campaign_id":       self.campaign_id,
            "min_age":           self.min_age,
            "max_age":           self.max_age,
            "gender":            self.gender,
            "income_min":        str(self.income_min) if self.income_min is not None else None,
            "income_max":        str(self.income_max) if self.income_max is not None else None,
            "occupation":        self.occupation,
            "education":         self.education,
            "life_stage":        self.life_stage,
            "geography":         self.geography,
            "origin":            self.origin,
            "interests":         self.interests,
            "lifestyle":         self.lifestyle,
            "purchase_behavior": self.purchase_behavior,
            "audience_size":     self.audience_size,
            "description":       self.description,
            "created_at":        self.created_at.isoformat() if self.created_at else None,
            "updated_at":        self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class CampaignProps:
    id: int
    campaign_id: int
    stalls: int = 0
    tables: int = 0
    chairs: int = 0
    led: int = 0
    banners: int = 0
    other_requirements: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row: dict) -> "CampaignProps":
        return cls(
            id=row["id"],
            campaign_id=row["campaign_id"],
            stalls=row.get("stalls", 0),
            tables=row.get("tables", 0),
            chairs=row.get("chairs", 0),
            led=row.get("led", 0),
            banners=row.get("banners", 0),
            other_requirements=row.get("other_requirements"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id":                 self.id,
            "campaign_id":        self.campaign_id,
            "stalls":             self.stalls,
            "tables":             self.tables,
            "chairs":             self.chairs,
            "led":                self.led,
            "banners":            self.banners,
            "other_requirements": self.other_requirements,
            "created_at":         self.created_at.isoformat() if self.created_at else None,
            "updated_at":         self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class CampaignMatchingRules:
    id: int
    campaign_id: int
    location_rule: str = "soft"
    language_rule: str = "soft"
    industry_rule: str = "soft"
    experience_rule: str = "soft"
    output_rule: str = "soft"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row: dict) -> "CampaignMatchingRules":
        from .enum import MATCHING_RULE
        return cls(
            id=row["id"],
            campaign_id=row["campaign_id"],
            location_rule=MATCHING_RULE.get(row.get("location_rule"), "soft"),
            language_rule=MATCHING_RULE.get(row.get("language_rule"), "soft"),
            industry_rule=MATCHING_RULE.get(row.get("industry_rule"), "soft"),
            experience_rule=MATCHING_RULE.get(row.get("experience_rule"), "soft"),
            output_rule=MATCHING_RULE.get(row.get("output_rule"), "soft"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def to_dict(self) -> dict:
        return {
            "id":              self.id,
            "campaign_id":     self.campaign_id,
            "location_rule":   self.location_rule,
            "language_rule":   self.language_rule,
            "industry_rule":   self.industry_rule,
            "experience_rule": self.experience_rule,
            "output_rule":     self.output_rule,
            "created_at":      self.created_at.isoformat() if self.created_at else None,
            "updated_at":      self.updated_at.isoformat() if self.updated_at else None,
        }


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
    city_id: Optional[int] = None
    city_name: Optional[str] = None
    locality: Optional[str] = None
    date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    total_hours: Optional[Decimal] = None

    products: List[Dict[str, Any]] = field(default_factory=list)
    industries: List[Dict[str, Any]] = field(default_factory=list)
    types: List[Dict[str, Any]] = field(default_factory=list)
    venues: List[Dict[str, Any]] = field(default_factory=list)
    audience: Optional[Dict[str, Any]] = None
    languages: List[Dict[str, Any]] = field(default_factory=list)
    props: Optional[Dict[str, Any]] = None
    matching_rules: Optional[Dict[str, Any]] = None

    @classmethod
    def from_row(
        cls,
        row: dict,
        products: Optional[List[dict]] = None,
        industries: Optional[List[dict]] = None,
        types: Optional[List[dict]] = None,
        venues: Optional[List[dict]] = None,
        audience: Optional[dict] = None,
        languages: Optional[List[dict]] = None,
        props: Optional[dict] = None,
        matching_rules: Optional[dict] = None,
    ) -> "Campaign":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            description=row.get("description"),
            city_id=row.get("city_id"),
            city_name=row.get("city_name"),
            locality=row.get("locality"),
            date=row.get("date"),
            start_time=row.get("start_time"),
            end_time=row.get("end_time"),
            total_hours=row.get("total_hours"),
            status=STATUS.get(row["status"], "draft"),
            is_deleted=row["is_deleted"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            products=products or [],
            industries=industries or [],
            types=types or [],
            venues=venues or [],
            audience=audience,
            languages=languages or [],
            props=props,
            matching_rules=matching_rules,
        )

    def to_dict(self) -> dict:
        return {
            "id":             self.id,
            "user_id":        self.user_id,
            "title":          self.title,
            "description":    self.description,
            "city_id":        self.city_id,
            "city_name":      self.city_name,
            "locality":       self.locality,
            "date":           self.date.isoformat() if self.date else None,
            "start_time":     self.start_time.isoformat() if self.start_time else None,
            "end_time":       self.end_time.isoformat() if self.end_time else None,
            "total_hours":    str(self.total_hours) if self.total_hours is not None else None,
            "status":         self.status,
            "products":       self.products,
            "industries":     self.industries,
            "types":          self.types,
            "venues":         self.venues,
            "audience":       self.audience,
            "languages":      self.languages,
            "props":          self.props,
            "matching_rules": self.matching_rules,
            "created_at":     self.created_at.isoformat() if self.created_at else None,
            "updated_at":     self.updated_at.isoformat() if self.updated_at else None,
        }


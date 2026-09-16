"""
Matching Models — Python Dataclasses
--------------------------------------
Plain data containers mirroring matching scores and persistent records.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List

from .enum import MATCH_STATUS


@dataclass
class MatchScoreBreakdown:
    location_score: float = 0.0
    language_score: float = 0.0
    industry_score: float = 0.0
    skills_score: float = 0.0
    ai_experience_score: float = 0.0
    total_score: float = 0.0
    is_eligible: bool = True
    ai_reasoning: Optional[str] = None
    disqualification_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_score":              round(self.total_score, 2),
            "location_score":           round(self.location_score, 2),
            "language_score":           round(self.language_score, 2),
            "industry_score":           round(self.industry_score, 2),
            "skills_score":             round(self.skills_score, 2),
            "ai_experience_score":      round(self.ai_experience_score, 2),
            "is_eligible":              self.is_eligible,
            "ai_reasoning":             self.ai_reasoning,
            "disqualification_reasons": self.disqualification_reasons,
        }


@dataclass
class CampaignProviderMatch:
    id: int
    campaign_id: int
    provider_id: int
    total_score: Decimal
    location_score: Decimal
    language_score: Decimal
    industry_score: Decimal
    skills_score: Decimal
    ai_experience_score: Decimal
    is_eligible: bool
    match_status: str
    created_at: datetime
    updated_at: datetime
    ai_reasoning: Optional[str] = None
    provider: Optional[Dict[str, Any]] = None

    @classmethod
    def from_row(cls, row: dict, provider: Optional[dict] = None) -> "CampaignProviderMatch":
        return cls(
            id=row["id"],
            campaign_id=row["campaign_id"],
            provider_id=row["provider_id"],
            total_score=row["total_score"],
            location_score=row.get("location_score", Decimal("0.00")),
            language_score=row.get("language_score", Decimal("0.00")),
            industry_score=row.get("industry_score", Decimal("0.00")),
            skills_score=row.get("skills_score", Decimal("0.00")),
            ai_experience_score=row.get("ai_experience_score", Decimal("0.00")),
            ai_reasoning=row.get("ai_reasoning"),
            is_eligible=row.get("is_eligible", True),
            match_status=MATCH_STATUS.get(row.get("match_status", 1), "matched"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            provider=provider,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id":                  self.id,
            "campaign_id":         self.campaign_id,
            "provider_id":         self.provider_id,
            "total_score":         float(self.total_score),
            "location_score":      float(self.location_score),
            "language_score":      float(self.language_score),
            "industry_score":      float(self.industry_score),
            "skills_score":        float(self.skills_score),
            "ai_experience_score": float(self.ai_experience_score),
            "ai_reasoning":        self.ai_reasoning,
            "is_eligible":         self.is_eligible,
            "match_status":        self.match_status,
            "provider":            self.provider,
            "created_at":          self.created_at.isoformat() if self.created_at else None,
            "updated_at":          self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class CampaignMatchWeights:
    id: int
    campaign_id: int
    location_weight: Decimal
    language_weight: Decimal
    industry_weight: Decimal
    skills_weight: Decimal
    ai_experience_weight: Decimal
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "CampaignMatchWeights":
        return cls(
            id=row["id"],
            campaign_id=row["campaign_id"],
            location_weight=row.get("location_weight", Decimal("0.20")),
            language_weight=row.get("language_weight", Decimal("0.20")),
            industry_weight=row.get("industry_weight", Decimal("0.15")),
            skills_weight=row.get("skills_weight", Decimal("0.20")),
            ai_experience_weight=row.get("ai_experience_weight", Decimal("0.25")),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id":                   self.id,
            "campaign_id":          self.campaign_id,
            "location_weight":      float(self.location_weight),
            "language_weight":      float(self.language_weight),
            "industry_weight":      float(self.industry_weight),
            "skills_weight":        float(self.skills_weight),
            "ai_experience_weight": float(self.ai_experience_weight),
            "created_at":           self.created_at.isoformat() if self.created_at else None,
            "updated_at":           self.updated_at.isoformat() if self.updated_at else None,
        }


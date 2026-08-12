"""
Payment Models — Python Dataclasses
--------------------------------------
Plain data containers mirroring the `payments` table.
DB schema is defined in schema.sql.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Payment:
    id: int
    user_id: int
    amount: Decimal
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime
    gateway: Optional[str] = None
    gateway_payment_id: Optional[str] = None
    gateway_order_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None

    @classmethod
    def from_row(cls, row: dict) -> "Payment":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            amount=row["amount"],
            currency=row["currency"],
            status=row["status"],
            gateway=row.get("gateway"),
            gateway_payment_id=row.get("gateway_payment_id"),
            gateway_order_id=row.get("gateway_order_id"),
            description=row.get("description"),
            metadata=row.get("metadata"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id":                 self.id,
            "user_id":            self.user_id,
            "amount":             str(self.amount),
            "currency":           self.currency,
            "status":             self.status,
            "gateway":            self.gateway,
            "gateway_payment_id": self.gateway_payment_id,
            "description":        self.description,
            "metadata":           self.metadata or {},
            "created_at":         self.created_at.isoformat() if self.created_at else None,
            "updated_at":         self.updated_at.isoformat() if self.updated_at else None,
        }

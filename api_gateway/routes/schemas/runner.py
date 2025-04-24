from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import (
    BaseModel,
    Field,
    PositiveFloat,
    PositiveInt,
    field_validator,
    ConfigDict,
)
from dateutil import parser as dtparser


class RunnerCreate(BaseModel):
    # ─────────── fields expected from UI ───────────
    id: Optional[int] = None              # ignored by backend
    created_at: Optional[datetime] = None # ignored by backend

    name: str
    strategy: str
    budget: PositiveFloat
    stock: str
    time_frame: PositiveInt
    stop_loss: float                      # may be negative
    take_profit: PositiveFloat

    time_range_from: Optional[datetime] = None
    time_range_to:   Optional[datetime] = None

    commission_ratio: Optional[float] = None
    exit_strategy: str
    activation: str = "active"

    # accept unknown keys but ignore them
    model_config = ConfigDict(extra="ignore")

    # ─────────── validators ───────────
    @field_validator("stock")
    @classmethod
    def _upper_ticker(cls, v: str) -> str:
        return v.upper()

    @field_validator(
        "time_range_from",
        "time_range_to",
        "created_at",
        mode="before",
    )
    @classmethod
    def _parse_dt(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        if isinstance(v, datetime):
            return v
        try:
            return dtparser.parse(v)
        except Exception as exc:
            raise ValueError(f"Invalid datetime value: {v!r}") from exc

    @field_validator("commission_ratio", mode="before")
    @classmethod
    def _float_or_none(cls, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        try:
            return float(v)
        except Exception:
            raise ValueError("commission_ratio must be a float or null")


class RunnerIds(BaseModel):
    ids: List[int] = Field(..., min_items=1, description="Runner IDs to act on")

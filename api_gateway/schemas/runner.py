from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RunnerCreate(BaseModel):
    symbol: str
    is_active: Optional[bool] = True
    stock_symbol: str
    strategy_name: str
    time_frame: int
    max_loss_perc: int
    take_profit_perc: int
    date_range: str
    stock_number_limit: int

class RunnerResponse(RunnerCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

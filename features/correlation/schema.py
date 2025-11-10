from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from .model import StockTrend


class StockCorrelationBase(BaseModel):
    base_stock_code: str = Field(..., description="기준 종목 코드")
    trend_type: StockTrend = Field(..., description="급등/급락 여부")
    correlated_stock_code: str = Field(..., description="상관관계 종목 코드")
    correlated_stock_name: str = Field(..., description="상관관계 종목명")
    correlation_rank: int = Field(..., description="상관관계 순위")
    correlation_value: Decimal = Field(..., description="상관계수")
    target_date: date = Field(..., description="조회 날짜")


class StockCorrelationCreate(StockCorrelationBase):
    pass

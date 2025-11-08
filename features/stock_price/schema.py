from decimal import Decimal

from pydantic import BaseModel, Field


class StockPriceBase(BaseModel):
    stock_code: str = Field(..., description="종목 코드")
    stock_name: str = Field(..., description="종목명")
    change_rate: Decimal = Field(..., description="등락률")


class StockPriceCreate(StockPriceBase):
    pass

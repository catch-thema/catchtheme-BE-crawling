from typing import List

from sqlalchemy.orm import Session

from .model import StockPriceHistory
from .schema import StockPriceCreate


class StockPriceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_batch(self, stock_prices: List[StockPriceCreate]) -> int:
        stock_price_models = [
            StockPriceHistory(**stock_price.model_dump())
            for stock_price in stock_prices
        ]

        try:
            self.db.bulk_save_objects(stock_price_models)
            self.db.commit()
            return len(stock_price_models)
        except Exception as e:
            self.db.rollback()
            raise e

    def find_surge_stocks(self, threshold: float = 5.0) -> List[StockPriceHistory]:
        return (
            self.db.query(StockPriceHistory)
            .filter(StockPriceHistory.change_rate >= threshold)
            .order_by(StockPriceHistory.change_rate.desc())
            .all()
        )

    def find_plunge_stocks(self, threshold: float = -5.0) -> List[StockPriceHistory]:
        return (
            self.db.query(StockPriceHistory)
            .filter(StockPriceHistory.change_rate <= threshold)
            .order_by(StockPriceHistory.change_rate.asc())
            .all()
        )

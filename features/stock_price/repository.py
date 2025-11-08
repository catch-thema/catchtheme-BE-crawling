from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_, func
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

    def find_stocks_by_abs_change_rate(
        self, threshold: float, target_date: Optional[datetime] = None
    ) -> List[str]:
        """
        등락률의 절댓값이 threshold% 이상인 종목의 종목코드를 반환합니다.

        Args:
            threshold: 등락률 임계값 (예: 5.0은 ±5% 이상)
            target_date: 조회할 날짜 (None일 경우 전체 조회)

        Returns:
            종목코드 리스트
        """
        query = self.db.query(StockPriceHistory.stock_code).filter(
            or_(
                StockPriceHistory.change_rate >= threshold,
                StockPriceHistory.change_rate <= -threshold,
            )
        )

        if target_date:
            # target_date의 시작 시간(00:00:00)부터 끝 시간(23:59:59)까지 조회
            start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = target_date.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
            query = query.filter(
                StockPriceHistory.created_at >= start_of_day,
                StockPriceHistory.created_at <= end_of_day,
            )

        stocks = query.distinct().all()

        return [stock[0] for stock in stocks]

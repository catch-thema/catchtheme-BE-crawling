from typing import List

from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session

from config.timezone import get_kst_now
from .model import StockCorrelation
from .schema import StockCorrelationCreate


class CorrelationRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_batch(self, correlations: List[StockCorrelationCreate]) -> int:

        if not correlations:
            return 0

        try:
            correlation_dicts = [
                correlation.model_dump() for correlation in correlations
            ]

            stmt = insert(StockCorrelation).values(correlation_dicts)

            update_dict = {
                "correlated_stock_name": stmt.inserted.correlated_stock_name,
                "correlation_rank": stmt.inserted.correlation_rank,
                "correlation_value": stmt.inserted.correlation_value,
                "created_at": get_kst_now(),
            }

            stmt = stmt.on_duplicate_key_update(**update_dict)

            self.db.execute(stmt)
            self.db.commit()

            return len(correlation_dicts)
        except Exception as e:
            self.db.rollback()
            raise e

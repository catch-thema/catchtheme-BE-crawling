from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from config.constants import DateFormats
from .krx_client import KRXClient
from .repository import StockPriceRepository
from .schema import StockPriceCreate
from .model import StockPriceHistory


class StockPriceService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = StockPriceRepository(db)
        self.krx_client = KRXClient()

    def fetch_and_save_stock_prices(self, target_date: str = None) -> int:
        if target_date is None:
            target_date = datetime.now().strftime(DateFormats.KRX_DATE_FORMAT)

        stock_data_list = self.krx_client.fetch_all_stock_prices(target_date)

        if not stock_data_list:
            return 0

        stock_price_creates = [
            StockPriceCreate(**stock_data) for stock_data in stock_data_list
        ]

        saved_count = self.repository.create_batch(stock_price_creates)
        return saved_count

    def get_surge_and_plunge_stocks(
        self, surge_threshold: float = 5.0, plunge_threshold: float = -5.0
    ) -> List[StockPriceHistory]:
        surge_stocks = self.repository.find_surge_stocks(surge_threshold)
        plunge_stocks = self.repository.find_plunge_stocks(plunge_threshold)
        return surge_stocks + plunge_stocks

from datetime import datetime

from config.database import engine, Base, SessionLocal
from config.constants import DateFormats
from features.stock_price.service import StockPriceService


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def run_stock_price_crawling(target_date: str = None):
    if target_date is None:
        target_date = datetime.now().strftime(DateFormats.KRX_DATE_FORMAT)

    db = SessionLocal()
    try:
        service = StockPriceService(db)

        print(f"[{target_date}] Starting stock price crawling...")
        saved_count = service.fetch_and_save_stock_prices(target_date)
        print(f"[{target_date}] Successfully saved {saved_count} stock prices")

        print("Fetching surge and plunge stocks...")
        volatile_stocks = service.get_surge_and_plunge_stocks()
        print(f"Found {len(volatile_stocks)} volatile stocks")

        return volatile_stocks
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()
    run_stock_price_crawling()

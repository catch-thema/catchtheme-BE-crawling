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

        # target_date 문자열을 datetime 객체로 변환
        target_datetime = datetime.strptime(target_date, DateFormats.KRX_DATE_FORMAT)

        print(f"Fetching volatile stocks for {target_date} (abs change rate >= 5%)...")
        threshold = 5.0
        volatile_stock_codes = service.get_stock_codes_by_abs_change_rate(
            threshold, target_datetime
        )
        print(f"Found {len(volatile_stock_codes)} volatile stocks")
        print(f"Stock codes: {volatile_stock_codes}")

        return volatile_stock_codes
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()
    run_stock_price_crawling()

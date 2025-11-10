from datetime import datetime

from config.database import engine, Base, SessionLocal
from config.constants import DateFormats
from features.stock_price.service import StockPriceService
from features.correlation.service import CorrelationService
from features.correlation.model import StockTrend


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def run_stock_price_crawling(target_date: str = None):
    if target_date is None:
        target_date = datetime.now().strftime(DateFormats.KRX_DATE_FORMAT)

    db = SessionLocal()
    try:
        stock_service = StockPriceService(db)
        correlation_service = CorrelationService(db)

        # 1. 주가 데이터 수집
        print(f"[{target_date}] Starting stock price crawling...")
        saved_count = stock_service.fetch_and_save_stock_prices(target_date)
        print(f"[{target_date}] Successfully saved {saved_count} stock prices")

        # target_date 문자열을 datetime 객체로 변환
        target_datetime = datetime.strptime(target_date, DateFormats.KRX_DATE_FORMAT)
        target_date_obj = target_datetime.date()

        # 2. 급등/급락 종목 조회
        threshold = 9.0
        print(
            f"\nFetching surge stocks for {target_date} (change rate >= +{threshold}%)..."
        )
        surge_stock_codes = stock_service.get_surge_stock_codes(
            threshold, target_datetime
        )
        print(f"Found {len(surge_stock_codes)} surge stocks")
        print(f"Surge stock codes: {surge_stock_codes}")

        print(
            f"\nFetching plunge stocks for {target_date} (change rate <= -{threshold}%)..."
        )
        plunge_stock_codes = stock_service.get_plunge_stock_codes(
            threshold, target_datetime
        )
        print(f"Found {len(plunge_stock_codes)} plunge stocks")
        print(f"Plunge stock codes: {plunge_stock_codes}")

        # 3. 급등 종목의 상관관계 데이터 수집
        if surge_stock_codes:
            print(f"\nFetching correlations for surge stocks...")
            surge_corr_count = correlation_service.fetch_and_save_correlations(
                surge_stock_codes, StockTrend.SURGE, target_date_obj
            )
            print(f"Saved {surge_corr_count} surge correlation records")

        # 4. 급락 종목의 상관관계 데이터 수집
        if plunge_stock_codes:
            print(f"\nFetching correlations for plunge stocks...")
            plunge_corr_count = correlation_service.fetch_and_save_correlations(
                plunge_stock_codes, StockTrend.PLUNGE, target_date_obj
            )
            print(f"Saved {plunge_corr_count} plunge correlation records")

        return {"surge": surge_stock_codes, "plunge": plunge_stock_codes}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()
    run_stock_price_crawling()

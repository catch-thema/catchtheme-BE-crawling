from datetime import datetime

from config.database import engine, Base, SessionLocal
from config.constants import DateFormats
from features.stock_price.service import StockPriceService
from features.stock_price.model import StockPriceHistory
from features.correlation.service import CorrelationService
from features.correlation.model import StockTrend, StockCorrelation
from features.stock_code_mapping.service import StockCodeMappingService
from features.stock_code_mapping.model import StockCodeMapping


def initialize_database():
    """데이터베이스 테이블 초기화 (모든 모델을 import해야 함)"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


def initialize_stock_code_mapping():
    """종목 코드 매핑 테이블 초기화 (최초 실행 시에만 수행)"""
    db = SessionLocal()
    try:
        mapping_service = StockCodeMappingService(db)
        mapping_service.initialize_stock_code_mappings()
    except Exception as e:
        print(f"Error initializing stock code mapping: {e}")
        raise
    finally:
        db.close()


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

        # 2. 급등/급락 종목 조회 (거래대금 10억 이상 필터링)
        threshold = 6.0
        min_trading_value = 1_000_000_000
        print(
            f"\nFetching surge stocks for {target_date} "
            f"(change rate >= +{threshold}%, trading value >= {min_trading_value:,})..."
        )
        surge_stock_codes = stock_service.get_surge_stock_codes(
            threshold, target_datetime, min_trading_value
        )
        print(f"Found {len(surge_stock_codes)} surge stocks")
        print(f"Surge stock codes: {surge_stock_codes}")

        print(
            f"\nFetching plunge stocks for {target_date} "
            f"(change rate <= -{threshold}%, trading value >= {min_trading_value:,})..."
        )
        plunge_stock_codes = stock_service.get_plunge_stock_codes(
            threshold, target_datetime, min_trading_value
        )
        print(f"Found {len(plunge_stock_codes)} plunge stocks")
        print(f"Plunge stock codes: {plunge_stock_codes}")

        # 3. 급등 종목의 상관관계 데이터 수집 및 결과 생성
        all_correlations = []

        if surge_stock_codes:
            print(f"\nFetching and saving correlations for surge stocks...")
            surge_results = correlation_service.fetch_and_save_correlations(
                surge_stock_codes, StockTrend.SURGE, target_date_obj
            )
            all_correlations.extend(surge_results)
            print(f"Built {len(surge_results)} surge correlation results")

        # 4. 급락 종목의 상관관계 데이터 수집 및 결과 생성
        if plunge_stock_codes:
            print(f"\nFetching and saving correlations for plunge stocks...")
            plunge_results = correlation_service.fetch_and_save_correlations(
                plunge_stock_codes, StockTrend.PLUNGE, target_date_obj
            )
            all_correlations.extend(plunge_results)
            print(f"Built {len(plunge_results)} plunge correlation results")

        print(f"\n=== Total correlation results: {len(all_correlations)} ===")
        # print(f"\n=== All Correlations (Raw List) ===")
        # print(all_correlations)

        return {"correlations": [result.model_dump() for result in all_correlations]}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()
    initialize_stock_code_mapping()
    run_stock_price_crawling()

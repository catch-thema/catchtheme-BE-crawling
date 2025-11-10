from datetime import datetime

from config.database import SessionLocal
from config.constants import DateFormats
from features.correlation.service import CorrelationService
from features.correlation.model import StockTrend


def test_correlation_crawling(stock_codes: list = None, target_date: str = None):
    if target_date is None:
        target_date = datetime.now().strftime(DateFormats.KRX_DATE_FORMAT)

    if stock_codes is None:
        # 테스트용 종목 코드 (삼성전자, SK하이닉스)
        stock_codes = ["005930", "000660"]

    target_date_obj = datetime.strptime(target_date, DateFormats.KRX_DATE_FORMAT).date()

    db = SessionLocal()
    try:
        service = CorrelationService(db)

        print(f"\n[{target_date}] 급등 종목 상관관계 데이터 수집 테스트")
        print(f"대상 종목: {stock_codes}")

        saved_count = service.fetch_and_save_correlations(
            stock_codes, StockTrend.SURGE, target_date_obj
        )

        print(f"\n총 {saved_count}개의 상관관계 레코드가 저장되었습니다.")

        return saved_count
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # 테스트 실행
    test_correlation_crawling()

    # 또는 특정 종목과 날짜로 테스트
    # test_correlation_crawling(["005930"], "20250108")

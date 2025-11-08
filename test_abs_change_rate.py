from datetime import datetime

from config.database import SessionLocal
from config.constants import DateFormats
from features.stock_price.service import StockPriceService


def test_find_stocks_by_abs_change_rate(target_date: str = None):
    """등락률 절댓값 기준 종목 조회 테스트"""
    if target_date is None:
        target_date = datetime.now().strftime(DateFormats.KRX_DATE_FORMAT)

    # target_date 문자열을 datetime 객체로 변환
    target_datetime = datetime.strptime(target_date, DateFormats.KRX_DATE_FORMAT)

    db = SessionLocal()
    try:
        service = StockPriceService(db)

        # 등락률의 절댓값이 5% 이상인 종목 조회
        threshold = 5.0
        stock_codes = service.get_stock_codes_by_abs_change_rate(
            threshold, target_datetime
        )

        print(f"\n[{target_date}] 등락률의 절댓값이 {threshold}% 이상인 종목:")
        print(f"총 {len(stock_codes)}개 종목")
        print(f"종목코드 목록: {stock_codes}")

        return stock_codes
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # 오늘 날짜로 테스트
    test_find_stocks_by_abs_change_rate()

    # 또는 특정 날짜로 테스트
    # test_find_stocks_by_abs_change_rate("20250108")

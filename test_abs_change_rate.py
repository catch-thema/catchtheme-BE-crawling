from datetime import datetime

from config.database import SessionLocal
from config.constants import DateFormats
from features.stock_price.service import StockPriceService


def test_find_surge_and_plunge_stocks(target_date: str = None):
    """급등/급락 종목 조회 테스트"""
    if target_date is None:
        target_date = datetime.now().strftime(DateFormats.KRX_DATE_FORMAT)

    # target_date 문자열을 datetime 객체로 변환
    target_datetime = datetime.strptime(target_date, DateFormats.KRX_DATE_FORMAT)

    db = SessionLocal()
    try:
        service = StockPriceService(db)
        threshold = 5.0

        # 급등 종목 조회
        print(f"\n[{target_date}] 등락률이 +{threshold}% 이상인 급등 종목:")
        surge_stock_codes = service.get_surge_stock_codes(threshold, target_datetime)
        print(f"총 {len(surge_stock_codes)}개 종목")
        print(f"급등 종목코드: {surge_stock_codes}")

        # 급락 종목 조회
        print(f"\n[{target_date}] 등락률이 -{threshold}% 이하인 급락 종목:")
        plunge_stock_codes = service.get_plunge_stock_codes(threshold, target_datetime)
        print(f"총 {len(plunge_stock_codes)}개 종목")
        print(f"급락 종목코드: {plunge_stock_codes}")

        # 전체 변동성 종목 조회 (옵션)
        print(f"\n[{target_date}] 등락률의 절댓값이 {threshold}% 이상인 전체 종목:")
        all_volatile_codes = service.get_stock_codes_by_abs_change_rate(
            threshold, target_datetime
        )
        print(f"총 {len(all_volatile_codes)}개 종목")

        return {
            "surge": surge_stock_codes,
            "plunge": plunge_stock_codes,
            "all": all_volatile_codes,
        }
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # 오늘 날짜로 테스트
    test_find_surge_and_plunge_stocks()

    # 또는 특정 날짜로 테스트
    # test_find_surge_and_plunge_stocks("20250108")

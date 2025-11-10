from datetime import date
from typing import List

from sqlalchemy.orm import Session

from .krx_correlation_client import KRXCorrelationClient
from .model import StockTrend
from .repository import CorrelationRepository
from .schema import StockCorrelationCreate


class CorrelationService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = CorrelationRepository(db)
        self.krx_client = KRXCorrelationClient()

    def fetch_and_save_correlations(
        self,
        stock_codes: List[str],
        trend_type: StockTrend,
        target_date: date,
        result_count: int = 200,
    ) -> int:
        """
        종목들의 상관관계 데이터를 조회하고 저장합니다.

        Args:
            stock_codes: 종목 코드 리스트
            trend_type: 급등/급락 여부
            target_date: 조회 날짜
            result_count: 조회할 상관관계 개수

        Returns:
            저장된 레코드 수
        """
        all_correlations = []

        for stock_code in stock_codes:
            print(
                f"  Fetching correlation data for {trend_type.value} stock: {stock_code}"
            )

            # KRX에서 상관관계 데이터 조회
            correlation_data_list = self.krx_client.fetch_correlation_data(
                stock_code, result_count
            )

            if not correlation_data_list:
                print(f"  No correlation data found for {stock_code}")
                continue

            # 스키마 객체로 변환
            for data in correlation_data_list:
                correlation_create = StockCorrelationCreate(
                    base_stock_code=stock_code,
                    trend_type=trend_type,
                    correlated_stock_code=data["correlated_stock_code"],
                    correlated_stock_name=data["correlated_stock_name"],
                    correlation_rank=data["rank"],
                    correlation_value=data["correlation_value"],
                    target_date=target_date,
                )
                all_correlations.append(correlation_create)

            print(f"  Found {len(correlation_data_list)} correlations for {stock_code}")

        # DB에 일괄 저장
        if all_correlations:
            saved_count = self.repository.create_batch(all_correlations)
            return saved_count

        return 0

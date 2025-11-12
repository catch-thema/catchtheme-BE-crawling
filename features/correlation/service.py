from datetime import date
from typing import List

from sqlalchemy.orm import Session

from .krx_correlation_client import KRXCorrelationClient
from .model import StockTrend
from .repository import CorrelationRepository
from .schema import (
    StockCorrelationCreate,
    CorrelationSummary,
    CorrelationSaveResponse,
)


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
        result_count: int = 20,
    ) -> CorrelationSaveResponse:
        all_correlations = []

        for stock_code in stock_codes:
            print(
                f"  Fetching correlation data for {trend_type.value} stock: {stock_code}"
            )

            correlation_data_list = self.krx_client.fetch_correlation_data(
                stock_code, result_count
            )

            if not correlation_data_list:
                print(f"  No correlation data found for {stock_code}")
                continue

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

        if not all_correlations:
            return CorrelationSaveResponse(
                saved_count=0,
                correlation_summaries=[],
            )

        saved_count = self.repository.create_batch(all_correlations)
        correlation_summaries = self._extract_unique_summaries(
            all_correlations, trend_type
        )

        # ==============================================
        # 테스트용: 연관관계 결과가 (등락 구분, 종목명) 쌍으로 출력됨
        # ==============================================
        # print("\n=== Correlation Summaries for Team ===")
        # for idx, summary in enumerate(correlation_summaries, 1):
        #     print(
        #         f"{idx}. trend_type: {summary.trend_type.value}, "
        #         f"stock_name: {summary.correlated_stock_name}"
        #     )
        # print(f"Total: {len(correlation_summaries)} unique stocks\n")

        return CorrelationSaveResponse(
            saved_count=saved_count,
            correlation_summaries=correlation_summaries,
        )

    def _extract_unique_summaries(
        self,
        correlations: List[StockCorrelationCreate],
        trend_type: StockTrend,
    ) -> List[CorrelationSummary]:
        unique_stock_names = {
            correlation.correlated_stock_name for correlation in correlations
        }

        return [
            CorrelationSummary(
                trend_type=trend_type,
                correlated_stock_name=stock_name,
            )
            for stock_name in sorted(unique_stock_names)
        ]

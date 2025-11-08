from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Index, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base
from config.constants import DatabaseTables


class StockPriceHistory(Base):
    __tablename__ = DatabaseTables.STOCK_PRICE_HISTORY

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    stock_code: Mapped[str] = mapped_column(String(20), nullable=False)
    stock_name: Mapped[str] = mapped_column(String(100), nullable=False)
    change_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        Index("idx_stock_code", "stock_code"),
        Index("idx_created_at", "created_at"),
        Index("idx_change_rate", "change_rate"),
    )

from config.database import engine, Base, SessionLocal
from features.stock_price.model import StockPriceHistory
from features.correlation.model import StockCorrelation


def reset_database():
    """모든 테이블 삭제 후 재생성"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped successfully")

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully")

    print("\nDatabase reset completed!")

if __name__ == "__main__":
    reset_database()

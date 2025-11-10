"""
데이터베이스를 초기화하는 스크립트
- 모든 테이블을 삭제하고 다시 생성합니다.
"""
from config.database import engine, Base, SessionLocal
from features.stock_price.model import StockPriceHistory


def reset_database():
    """모든 테이블 삭제 후 재생성"""
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("All tables dropped successfully")

    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully")

    print("\nDatabase reset completed!")


def clear_stock_price_data():
    """stock_price_history 테이블의 데이터만 삭제 (테이블 구조는 유지)"""
    db = SessionLocal()
    try:
        print("Clearing stock_price_history table...")
        deleted_count = db.query(StockPriceHistory).delete()
        db.commit()
        print(f"Deleted {deleted_count} records from stock_price_history table")
        print("Data cleared successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--clear-data":
        # 데이터만 삭제 (테이블 구조 유지)
        clear_stock_price_data()
    else:
        # 테이블 삭제 후 재생성
        reset_database()

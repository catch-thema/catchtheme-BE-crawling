"""
컨테이너 시작 시 한 번만 실행되는 DB 초기화 스크립트
"""
from main import initialize_database

if __name__ == "__main__":
    initialize_database()

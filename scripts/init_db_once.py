"""
컨테이너 시작 시 한 번만 실행되는 DB 초기화 스크립트
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import initialize_database

if __name__ == "__main__":
    initialize_database()

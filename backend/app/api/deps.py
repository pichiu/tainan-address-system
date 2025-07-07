"""
API 依賴注入模組
"""
from typing import Generator
from sqlalchemy.orm import Session
from app.core.database import SessionLocal


def get_db() -> Generator:
    """
    取得資料庫連線
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
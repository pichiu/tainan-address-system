"""
應用設定檔
"""
from pydantic_settings import BaseSettings
from typing import List, Union
import os


class Settings(BaseSettings):
    """應用設定類別"""
    
    # 基本設定
    PROJECT_NAME: str = "臺南市門牌坐標查詢系統"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # 資料庫設定
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/tainan_addresses"
    
    # Supabase 設定 (如果使用)
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    
    # CORS 設定
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://localhost:3000",
        "https://localhost:3001",
    ]
    
    # 安全設定
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 分頁設定
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 1000
    
    # 快取設定
    CACHE_TTL: int = 3600  # 1小時
    
    # 地理設定
    DEFAULT_SRID: int = 4326  # WGS84
    TAIWAN_BOUNDS: dict = {
        "min_lat": 21.8,
        "max_lat": 25.3,
        "min_lng": 119.3,
        "max_lng": 122.0
    }
    
    # 搜尋設定
    SEARCH_MIN_LENGTH: int = 2
    SEARCH_MAX_RESULTS: int = 100
    
    # 效能設定
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # 日誌設定
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 建立全域設定實例
settings = Settings()


# 開發環境特定設定
if os.getenv("ENVIRONMENT") == "development":
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"
    settings.BACKEND_CORS_ORIGINS.extend([
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ])


# 生產環境特定設定
if os.getenv("ENVIRONMENT") == "production":
    settings.DEBUG = False
    settings.LOG_LEVEL = "WARNING"


def get_database_url() -> str:
    """取得資料庫連線字串"""
    if settings.SUPABASE_URL and settings.SUPABASE_KEY:
        # 使用 Supabase
        # 注意：這裡需要將 Supabase URL 轉換為 PostgreSQL 連線字串
        # 格式通常是: postgresql://[username]:[password]@[host]:[port]/[database]
        return settings.DATABASE_URL
    else:
        # 使用一般 PostgreSQL
        return settings.DATABASE_URL


def get_cors_origins() -> List[Union[str, str]]:
    """取得 CORS 允許的來源"""
    if isinstance(settings.BACKEND_CORS_ORIGINS, str):
        return [origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",")]
    return settings.BACKEND_CORS_ORIGINS


# 更新 settings 中的 CORS 設定
settings.BACKEND_CORS_ORIGINS = get_cors_origins()


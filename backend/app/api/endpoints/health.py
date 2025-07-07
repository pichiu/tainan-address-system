"""
健康檢查 API 端點
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import check_database_connection, get_database_stats
from app.api.deps import get_db
from app.core.config import settings
from app.schemas.address import HealthCheck, APIResponse

router = APIRouter()


@router.get("/", response_model=APIResponse)
async def health_check(db: Session = Depends(get_db)):
    """基本健康檢查"""
    try:
        # 檢查資料庫連線
        db_connected = await check_database_connection()
        
        # 取得資料庫統計
        db_stats = await get_database_stats()
        
        health_data = HealthCheck(
            status="healthy" if db_connected else "unhealthy",
            database=db_connected,
            version=settings.VERSION,
            timestamp=datetime.now(),
            database_stats=db_stats
        )
        
        return APIResponse(
            success=True,
            data=health_data.model_dump(),
            message="系統健康檢查完成"
        )
    
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            message="健康檢查失敗",
            error=str(e)
        )


@router.get("/detailed", response_model=APIResponse)
async def detailed_health_check(db: Session = Depends(get_db)):
    """詳細健康檢查"""
    try:
        # 基本系統資訊
        system_info = {
            "service_name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": "development" if settings.DEBUG else "production",
            "api_version": settings.API_V1_STR,
            "timestamp": datetime.now().isoformat()
        }
        
        # 資料庫連線檢查
        db_connected = await check_database_connection()
        db_stats = await get_database_stats()
        
        # 設定檢查
        config_info = {
            "cors_origins": settings.BACKEND_CORS_ORIGINS,
            "default_page_size": settings.DEFAULT_PAGE_SIZE,
            "max_page_size": settings.MAX_PAGE_SIZE,
            "cache_ttl": settings.CACHE_TTL
        }
        
        # 功能檢查
        features = {
            "address_search": True,
            "geo_search": True,  # 會在實際查詢時檢查 PostGIS
            "statistics": True,
            "export": True
        }
        
        detailed_data = {
            "system": system_info,
            "database": {
                "connected": db_connected,
                "stats": db_stats
            },
            "configuration": config_info,
            "features": features,
            "status": "healthy" if db_connected and db_stats.get("table_exists", False) else "degraded"
        }
        
        return APIResponse(
            success=True,
            data=detailed_data,
            message="詳細健康檢查完成"
        )
    
    except Exception as e:
        return APIResponse(
            success=False,
            data=None,
            message="詳細健康檢查失敗",
            error=str(e)
        )


@router.get("/readiness", response_model=APIResponse)
async def readiness_check(db: Session = Depends(get_db)):
    """就緒檢查 - 檢查服務是否準備好接受請求"""
    try:
        # 檢查資料庫是否可用
        db_connected = await check_database_connection()
        db_stats = await get_database_stats()
        
        # 檢查必要的資料表是否存在
        tables_ready = db_stats.get("table_exists", False)
        
        # 檢查是否有資料
        has_data = db_stats.get("total_addresses", 0) > 0
        
        ready = db_connected and tables_ready
        
        readiness_data = {
            "ready": ready,
            "database_connected": db_connected,
            "tables_exists": tables_ready,
            "has_data": has_data,
            "data_summary": {
                "addresses": db_stats.get("total_addresses", 0),
                "districts": db_stats.get("districts", 0),
                "villages": db_stats.get("villages", 0)
            }
        }
        
        return APIResponse(
            success=ready,
            data=readiness_data,
            message="服務就緒" if ready else "服務尚未就緒"
        )
    
    except Exception as e:
        return APIResponse(
            success=False,
            data={"ready": False, "error": str(e)},
            message="就緒檢查失敗",
            error=str(e)
        )


@router.get("/liveness", response_model=APIResponse)
async def liveness_check():
    """存活檢查 - 檢查服務是否還活著"""
    try:
        return APIResponse(
            success=True,
            data={
                "alive": True,
                "timestamp": datetime.now().isoformat(),
                "service": settings.PROJECT_NAME,
                "version": settings.VERSION
            },
            message="服務正常運行"
        )
    
    except Exception as e:
        return APIResponse(
            success=False,
            data={"alive": False},
            message="存活檢查失敗",
            error=str(e)
        )


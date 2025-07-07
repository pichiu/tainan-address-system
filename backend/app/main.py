"""
臺南市門牌坐標查詢系統 - FastAPI 主程式
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, create_tables
from app.api.endpoints import addresses, health

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用啟動和關閉時的生命週期管理"""
    # 啟動時執行
    logger.info("正在啟動應用...")
    await create_tables()
    logger.info("資料庫表格檢查完成")
    
    yield
    
    # 關閉時執行
    logger.info("正在關閉應用...")


# 建立 FastAPI 應用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="臺南市門牌坐標資料查詢 API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# 中介軟體設定
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 請求時間中介軟體
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# 全域異常處理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全域異常: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "message": "內部伺服器錯誤",
            "error": str(exc) if settings.DEBUG else "系統發生錯誤"
        }
    )


# 註冊路由
app.include_router(
    health.router,
    prefix=f"{settings.API_V1_STR}/health",
    tags=["健康檢查"]
)

app.include_router(
    addresses.router,
    prefix=f"{settings.API_V1_STR}",
    tags=["地址查詢"]
)


@app.get("/")
async def root():
    """根路由"""
    return {
        "success": True,
        "data": {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs_url": f"{settings.API_V1_STR}/docs"
        },
        "message": "歡迎使用臺南市門牌坐標查詢系統 API"
    }


@app.get(f"{settings.API_V1_STR}/license")
async def get_license():
    """取得資料授權資訊"""
    return {
        "success": True,
        "data": {
            "license": "政府資料開放授權條款－第1版",
            "source": "臺南市政府",
            "year": "113年",
            "dataset": "臺南市門牌坐標資料",
            "attribution": (
                "臺南市政府 113年 臺南市門牌坐標資料\n"
                "此開放資料依政府資料開放授權條款 (Open Government Data License) "
                "進行公眾釋出，使用者於遵守本條款各項規定之前提下，得利用之。"
            ),
            "license_url": "https://data.gov.tw/license",
            "terms": {
                "usage": "不限目的、時間及地域、非專屬、不可撤回、免授權金進行利用",
                "attribution_required": True,
                "commercial_use": True,
                "modification": True,
                "redistribution": True
            }
        },
        "message": "資料授權資訊"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )


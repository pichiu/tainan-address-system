"""
資料庫連線設定
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging

from app.core.config import settings, get_database_url

logger = logging.getLogger(__name__)

# 建立資料庫引擎
# 將 postgresql:// 轉換為 postgresql+psycopg://
database_url = get_database_url()
if database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://')

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # 連線前先 ping 檢查
    echo=settings.DEBUG,  # 開發環境下顯示 SQL
)

# 建立 Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 建立 Base 類別
Base = declarative_base()


# get_db 函數已移至 app.api.deps 模組


async def create_tables():
    """建立資料庫表格和索引"""
    try:
        with engine.connect() as conn:
            # 檢查並啟用 PostGIS 擴展
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
                logger.info("PostGIS 擴展已啟用")
            except Exception as e:
                logger.warning(f"無法啟用 PostGIS 擴展: {e}")
            
            # 建立地址資料表
            create_address_table = text("""
                CREATE TABLE IF NOT EXISTS addresses (
                    id BIGSERIAL PRIMARY KEY,
                    district VARCHAR(10) NOT NULL,
                    village VARCHAR(20) NOT NULL,
                    neighborhood INTEGER NOT NULL,
                    street VARCHAR(100),
                    area VARCHAR(50),
                    lane VARCHAR(20),
                    alley VARCHAR(20),
                    number VARCHAR(20),
                    x_coord DECIMAL(10, 6),
                    y_coord DECIMAL(10, 6),
                    full_address TEXT,
                    geom GEOMETRY(POINT, 4326),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            conn.execute(create_address_table)
            
            # 建立統計快取表
            create_stats_table = text("""
                CREATE TABLE IF NOT EXISTS address_stats (
                    id SERIAL PRIMARY KEY,
                    level VARCHAR(20) NOT NULL,
                    district VARCHAR(10),
                    village VARCHAR(20),
                    neighborhood INTEGER,
                    address_count INTEGER NOT NULL DEFAULT 0,
                    village_count INTEGER DEFAULT 0,
                    neighborhood_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT NOW(),
                    UNIQUE(level, district, village, neighborhood)
                );
            """)
            conn.execute(create_stats_table)
            
            # 建立索引
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_addresses_district ON addresses(district);",
                "CREATE INDEX IF NOT EXISTS idx_addresses_village ON addresses(district, village);",
                "CREATE INDEX IF NOT EXISTS idx_addresses_neighborhood ON addresses(district, village, neighborhood);",
                "CREATE INDEX IF NOT EXISTS idx_addresses_coords ON addresses(x_coord, y_coord);",
                "CREATE INDEX IF NOT EXISTS idx_addresses_full_address ON addresses(full_address);",
                "CREATE INDEX IF NOT EXISTS idx_stats_level ON address_stats(level);",
                "CREATE INDEX IF NOT EXISTS idx_stats_district ON address_stats(district);",
            ]
            
            # 如果 PostGIS 可用，建立空間索引
            try:
                indexes.extend([
                    "CREATE INDEX IF NOT EXISTS idx_addresses_geom ON addresses USING GIST(geom);",
                ])
                logger.info("空間索引已建立")
            except Exception as e:
                logger.warning(f"無法建立空間索引: {e}")
            
            # 建立全文搜尋索引（使用預設配置）
            try:
                indexes.append(
                    "CREATE INDEX IF NOT EXISTS idx_addresses_full_text ON addresses USING GIN(to_tsvector('simple', full_address));"
                )
                logger.info("全文搜尋索引已建立")
            except Exception as e:
                logger.warning(f"無法建立全文搜尋索引: {e}")
                # 使用三字組索引作為替代
                try:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
                    indexes.append(
                        "CREATE INDEX IF NOT EXISTS idx_addresses_text_simple ON addresses USING GIN(full_address gin_trgm_ops);"
                    )
                    logger.info("三字組索引已建立")
                except Exception as e2:
                    logger.warning(f"無法建立三字組索引: {e2}")
                    # 使用 B-tree 索引作為最後替代
                    indexes.append(
                        "CREATE INDEX IF NOT EXISTS idx_addresses_text_btree ON addresses(full_address text_pattern_ops);"
                    )
            
            # 執行所有索引建立
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                except Exception as e:
                    logger.warning(f"索引建立失敗: {index_sql}, 錯誤: {e}")
            
            # 建立觸發器更新 full_address
            create_trigger = text("""
                CREATE OR REPLACE FUNCTION update_full_address()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.full_address := CONCAT(
                        COALESCE(NEW.street, ''),
                        COALESCE(NEW.area, ''),
                        COALESCE(NEW.lane, ''),
                        COALESCE(NEW.alley, ''),
                        COALESCE(NEW.number, '')
                    );
                    
                    -- 更新地理座標
                    IF NEW.x_coord IS NOT NULL AND NEW.y_coord IS NOT NULL THEN
                        NEW.geom := ST_SetSRID(ST_MakePoint(NEW.x_coord, NEW.y_coord), 4326);
                    END IF;
                    
                    NEW.updated_at := NOW();
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                
                DROP TRIGGER IF EXISTS trigger_update_full_address ON addresses;
                CREATE TRIGGER trigger_update_full_address
                    BEFORE INSERT OR UPDATE ON addresses
                    FOR EACH ROW EXECUTE FUNCTION update_full_address();
            """)
            
            try:
                conn.execute(create_trigger)
                logger.info("觸發器已建立")
            except Exception as e:
                logger.warning(f"無法建立觸發器: {e}")
            
            conn.commit()
            logger.info("資料庫表格和索引建立完成")
            
    except Exception as e:
        logger.error(f"建立資料庫表格時發生錯誤: {e}")
        raise


async def check_database_connection():
    """檢查資料庫連線"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.fetchone()[0] == 1
    except Exception as e:
        logger.error(f"資料庫連線檢查失敗: {e}")
        return False


async def get_database_stats():
    """取得資料庫統計資訊"""
    try:
        with engine.connect() as conn:
            # 檢查表格是否存在
            table_check = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'addresses'
                );
            """)).fetchone()[0]
            
            if not table_check:
                return {
                    "table_exists": False,
                    "total_addresses": 0,
                    "districts": 0,
                    "villages": 0,
                    "neighborhoods": 0
                }
            
            # 取得統計資料
            stats = conn.execute(text("""
                SELECT 
                    COUNT(*) as total_addresses,
                    COUNT(DISTINCT district) as districts,
                    COUNT(DISTINCT CONCAT(district, '|', village)) as villages,
                    COUNT(DISTINCT CONCAT(district, '|', village, '|', neighborhood)) as neighborhoods
                FROM addresses;
            """)).fetchone()
            
            return {
                "table_exists": True,
                "total_addresses": stats[0],
                "districts": stats[1],
                "villages": stats[2],
                "neighborhoods": stats[3]
            }
            
    except Exception as e:
        logger.error(f"取得資料庫統計時發生錯誤: {e}")
        return {
            "error": str(e),
            "table_exists": False,
            "total_addresses": 0,
            "districts": 0,
            "villages": 0,
            "neighborhoods": 0
        }


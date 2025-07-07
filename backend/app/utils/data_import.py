"""
臺南市門牌資料匯入工具
"""
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
import logging
from tqdm import tqdm
import os
import argparse
from datetime import datetime
from pyproj import Transformer

from app.core.config import settings, get_database_url

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TainanAddressImporter:
    """臺南市門牌資料匯入器"""
    
    def __init__(self, database_url: str = None):
        """初始化匯入器"""
        self.database_url = database_url or get_database_url()
        self.engine = create_engine(self.database_url)
        self.transformer = Transformer.from_crs("EPSG:3826", "EPSG:4326", always_xy=True)
        
    def validate_csv_structure(self, file_path: str) -> bool:
        """驗證 CSV 檔案結構"""
        try:
            # 讀取前幾行來檢查欄位
            sample_df = pd.read_csv(file_path, nrows=5, encoding='utf-8')
            
            required_columns = ['區', '村里', '鄰', '橫座標', '縱座標']
            optional_columns = ['街、路段', '地區', '巷', '弄', '號']
            
            missing_required = [col for col in required_columns if col not in sample_df.columns]
            
            if missing_required:
                logger.error(f"缺少必要欄位: {missing_required}")
                return False
            
            logger.info("CSV 檔案結構驗證通過")
            logger.info(f"檔案欄位: {list(sample_df.columns)}")
            return True
            
        except Exception as e:
            logger.error(f"CSV 檔案結構驗證失敗: {e}")
            return False
    
    def transform_coords(self, row):
        try:
            x, y = float(row['x_coord']), float(row['y_coord'])
            lon, lat = self.transformer.transform(x, y)
            return pd.Series({'x_coord': lon, 'y_coord': lat})
        except:
            return pd.Series({'x_coord': None, 'y_coord': None})
    
    def to_halfwidth(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        return ''.join(
            chr(ord(c) - 0xFEE0) if '！' <= c <= '～' else c
            for c in text
        ).replace('　', ' ')

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清理和標準化資料"""
        logger.info("開始清理資料...")
        original_count = len(df)
        
        # 移除完全重複的資料
        df = df.drop_duplicates()
        logger.info(f"移除 {original_count - len(df)} 筆重複資料")
        
        # 處理空值
        df = df.fillna('')
        
        # 標準化欄位名稱
        column_mapping = {
            '區': 'district',
            '村里': 'village',
            '鄰': 'neighborhood',
            '街、路段': 'street',
            '地區': 'area',
            '巷': 'lane',
            '弄': 'alley',
            '號': 'number',
            '橫座標': 'x_coord',
            '縱座標': 'y_coord'
        }
        
        df = df.rename(columns=column_mapping)
        
        # 確保必要欄位存在
        for col in ['district', 'village', 'neighborhood', 'street', 'area', 'lane', 'alley', 'number']:
            if col not in df.columns:
                df[col] = ''
        
        # 清理鄰欄位 - 確保是整數
        df['neighborhood'] = pd.to_numeric(df['neighborhood'], errors='coerce').fillna(0).astype(int)
        
        for col in ['street', 'area', 'lane', 'alley', 'number']:
            if col in df.columns:
                df[col] = df[col].apply(self.to_halfwidth)

        df[['x_coord', 'y_coord']] = df.apply(self.transform_coords, axis=1)

        # 清理座標欄位
        df['x_coord'] = pd.to_numeric(df['x_coord'], errors='coerce')
        df['y_coord'] = pd.to_numeric(df['y_coord'], errors='coerce')
        
        # 移除座標異常的資料（台灣範圍外）
        coord_filter = (
            (df['x_coord'] >= 119.0) & (df['x_coord'] <= 122.5) &
            (df['y_coord'] >= 21.5) & (df['y_coord'] <= 25.5)
        )
        invalid_coords = len(df) - coord_filter.sum()
        if invalid_coords > 0:
            logger.warning(f"移除 {invalid_coords} 筆座標異常的資料")
            df = df[coord_filter]
        
        # 建立完整地址
        def build_full_address(row):
            parts = [
                str(row['street']) if pd.notna(row['street']) and row['street'] else '',
                str(row['area']) if pd.notna(row['area']) and row['area'] else '',
                str(row['lane']) if pd.notna(row['lane']) and row['lane'] else '',
                str(row['alley']) if pd.notna(row['alley']) and row['alley'] else '',
                str(row['number']) if pd.notna(row['number']) and row['number'] else ''
            ]
            return ''.join([part for part in parts if part])
        
        df['full_address'] = df.apply(build_full_address, axis=1)
        
        # 移除沒有任何地址資訊的資料
        empty_address_filter = (
            (df['district'] != '') & 
            (df['village'] != '') & 
            (df['neighborhood'] > 0)
        )
        invalid_address = len(df) - empty_address_filter.sum()
        if invalid_address > 0:
            logger.warning(f"移除 {invalid_address} 筆地址資訊不完整的資料")
            df = df[empty_address_filter]
        
        logger.info(f"資料清理完成，剩餘 {len(df)} 筆有效資料")
        return df
    
    def create_tables_if_not_exists(self):
        """建立資料表（如果不存在）"""
        logger.info("檢查並建立資料表...")
        
        create_sql = """
        -- 建立地址資料表
        CREATE TABLE IF NOT EXISTS addresses (
            id BIGSERIAL PRIMARY KEY,
            district VARCHAR(10) NOT NULL,
            village VARCHAR(20) NOT NULL,
            neighborhood INTEGER NOT NULL,
            street VARCHAR(100),
            area VARCHAR(50),
            lane VARCHAR(20),
            alley VARCHAR(20),
            number VARCHAR(50),
            x_coord DECIMAL(10, 6),
            y_coord DECIMAL(10, 6),
            full_address TEXT,
            geom GEOMETRY(POINT, 4326),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- 建立索引
        CREATE INDEX IF NOT EXISTS idx_addresses_district ON addresses(district);
        CREATE INDEX IF NOT EXISTS idx_addresses_village ON addresses(district, village);
        CREATE INDEX IF NOT EXISTS idx_addresses_neighborhood ON addresses(district, village, neighborhood);
        CREATE INDEX IF NOT EXISTS idx_addresses_coords ON addresses(x_coord, y_coord);
        """
        
        with self.engine.connect() as conn:
            conn.execute(text(create_sql))
            conn.commit()
        
        logger.info("資料表建立完成")
    
    def import_batch(self, df_batch: pd.DataFrame, batch_num: int):
        """匯入單一批次資料"""
        try:
            # 選擇需要的欄位
            columns_to_import = [
                'district', 'village', 'neighborhood', 'street', 'area',
                'lane', 'alley', 'number', 'x_coord', 'y_coord', 'full_address'
            ]
            
            df_batch = df_batch[columns_to_import]
            
            # 匯入到資料庫
            df_batch.to_sql(
                'addresses',
                self.engine,
                if_exists='append',
                index=False,
                method='multi',
                chunksize=1000
            )
            
            logger.info(f"批次 {batch_num} 匯入完成：{len(df_batch)} 筆資料")
            
        except Exception as e:
            logger.error(f"批次 {batch_num} 匯入失敗：{e}")
            raise
    
    def update_geometry_and_stats(self):
        """更新地理座標和統計資料"""
        logger.info("更新地理座標...")
        
        try:
            with self.engine.connect() as conn:
                # 更新地理座標
                update_geom_sql = """
                UPDATE addresses 
                SET geom = ST_SetSRID(ST_MakePoint(x_coord, y_coord), 4326)
                WHERE x_coord IS NOT NULL AND y_coord IS NOT NULL AND geom IS NULL;
                """
                result = conn.execute(text(update_geom_sql))
                logger.info(f"更新了 {result.rowcount} 筆地理座標")
                
                # 建立統計快取表
                create_stats_sql = """
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
                """
                conn.execute(text(create_stats_sql))
                
                # 更新統計資料
                update_stats_sql = """
                -- 清空舊統計
                TRUNCATE TABLE address_stats;
                
                -- 區級統計
                INSERT INTO address_stats (level, district, address_count, village_count, neighborhood_count)
                SELECT 
                    'district' as level,
                    district,
                    COUNT(*) as address_count,
                    COUNT(DISTINCT village) as village_count,
                    COUNT(DISTINCT CONCAT(village, '-', neighborhood)) as neighborhood_count
                FROM addresses
                GROUP BY district;
                
                -- 村里級統計
                INSERT INTO address_stats (level, district, village, address_count, neighborhood_count)
                SELECT 
                    'village' as level,
                    district,
                    village,
                    COUNT(*) as address_count,
                    COUNT(DISTINCT neighborhood) as neighborhood_count
                FROM addresses
                GROUP BY district, village;
                
                -- 鄰級統計
                INSERT INTO address_stats (level, district, village, neighborhood, address_count)
                SELECT 
                    'neighborhood' as level,
                    district,
                    village,
                    neighborhood,
                    COUNT(*) as address_count
                FROM addresses
                GROUP BY district, village, neighborhood;
                """
                
                conn.execute(text(update_stats_sql))
                conn.commit()
                
                logger.info("統計資料更新完成")
                
        except Exception as e:
            logger.error(f"更新地理座標和統計資料失敗：{e}")
            raise
    
    def import_csv(self, csv_file_path: str, chunk_size: int = 5000, clear_existing: bool = False):
        """匯入 CSV 檔案"""
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"找不到檔案：{csv_file_path}")
        
        # 驗證檔案結構
        if not self.validate_csv_structure(csv_file_path):
            raise ValueError("CSV 檔案結構不正確")
        
        # 建立資料表
        self.create_tables_if_not_exists()
        
        # 清空現有資料（如果需要）
        if clear_existing:
            logger.warning("清空現有資料...")
            with self.engine.connect() as conn:
                conn.execute(text("TRUNCATE TABLE addresses RESTART IDENTITY CASCADE"))
                conn.execute(text("TRUNCATE TABLE address_stats RESTART IDENTITY CASCADE"))
                conn.commit()
        
        # 計算總行數
        total_rows = sum(1 for line in open(csv_file_path, 'r', encoding='utf-8')) - 1
        logger.info(f"準備匯入 {total_rows:,} 筆資料")
        
        # 分批處理
        batch_num = 0
        total_imported = 0
        
        try:
            for chunk in tqdm(
                pd.read_csv(csv_file_path, chunksize=chunk_size, encoding='utf-8'),
                desc="匯入進度",
                unit="批次"
            ):
                batch_num += 1
                
                # 清理資料
                chunk_cleaned = self.clean_data(chunk)
                
                if len(chunk_cleaned) > 0:
                    # 匯入批次
                    self.import_batch(chunk_cleaned, batch_num)
                    total_imported += len(chunk_cleaned)
                else:
                    logger.warning(f"批次 {batch_num} 清理後無有效資料")
            
            logger.info(f"資料匯入完成！總共匯入 {total_imported:,} 筆資料")
            
            # 更新地理座標和統計
            self.update_geometry_and_stats()
            
            # 顯示最終統計
            self.show_import_summary()
            
        except Exception as e:
            logger.error(f"匯入過程發生錯誤：{e}")
            raise
    
    def show_import_summary(self):
        """顯示匯入摘要"""
        try:
            with self.engine.connect() as conn:
                stats = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_addresses,
                        COUNT(DISTINCT district) as total_districts,
                        COUNT(DISTINCT CONCAT(district, '|', village)) as total_villages,
                        COUNT(DISTINCT CONCAT(district, '|', village, '|', neighborhood)) as total_neighborhoods,
                        COUNT(CASE WHEN geom IS NOT NULL THEN 1 END) as addresses_with_geom
                    FROM addresses
                """)).fetchone()
                
                logger.info("=" * 50)
                logger.info("匯入摘要")
                logger.info("=" * 50)
                logger.info(f"總地址數量：{stats[0]:,}")
                logger.info(f"區數量：{stats[1]}")
                logger.info(f"村里數量：{stats[2]}")
                logger.info(f"鄰數量：{stats[3]}")
                logger.info(f"含地理座標：{stats[4]:,}")
                logger.info("=" * 50)
                
        except Exception as e:
            logger.error(f"取得匯入摘要失敗：{e}")


def main():
    """主程式"""
    parser = argparse.ArgumentParser(description='臺南市門牌資料匯入工具')
    parser.add_argument('csv_file', help='CSV 檔案路徑')
    parser.add_argument('--chunk-size', type=int, default=5000, help='批次大小 (預設: 5000)')
    parser.add_argument('--clear', action='store_true', help='清空現有資料')
    parser.add_argument('--database-url', help='資料庫連線字串')
    
    args = parser.parse_args()
    
    try:
        # 建立匯入器
        importer = TainanAddressImporter(args.database_url)
        
        # 開始匯入
        start_time = datetime.now()
        logger.info(f"開始匯入：{start_time}")
        
        importer.import_csv(
            csv_file_path=args.csv_file,
            chunk_size=args.chunk_size,
            clear_existing=args.clear
        )
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"匯入完成！耗時：{duration}")
        
    except Exception as e:
        logger.error(f"匯入失敗：{e}")
        exit(1)


if __name__ == "__main__":
    main()


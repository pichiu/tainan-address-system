"""
地址查詢業務邏輯服務
"""
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func, and_, or_
import math
import logging

from app.models.address import Address, AddressStats
from app.schemas.address import (
    AddressSummary, NeighborhoodDetail, SearchParams, 
    GeoSearchParams, PaginationInfo
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class AddressService:
    """地址查詢服務類別"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_districts(self) -> List[str]:
        """取得所有區的列表"""
        try:
            result = self.db.execute(text("""
                SELECT DISTINCT district
                FROM addresses 
                ORDER BY district
            """))
            return [row[0] for row in result]
        except Exception as e:
            logger.error(f"取得區列表失敗: {e}")
            raise
    
    def get_villages(self, district: str) -> List[str]:
        """取得指定區的所有村里"""
        try:
            result = self.db.execute(text("""
                SELECT DISTINCT village 
                FROM addresses 
                WHERE district = :district 
                ORDER BY village
            """), {"district": district})
            
            villages = [row[0] for row in result]
            if not villages:
                raise ValueError(f"區 '{district}' 不存在或無資料")
            
            return villages
        except Exception as e:
            logger.error(f"取得村里列表失敗: {e}")
            raise
    
    def get_neighborhoods(self, district: str, village: str) -> List[int]:
        """取得指定區村里的所有鄰"""
        try:
            result = self.db.execute(text("""
                SELECT DISTINCT neighborhood 
                FROM addresses 
                WHERE district = :district AND village = :village 
                ORDER BY neighborhood
            """), {"district": district, "village": village})
            
            neighborhoods = [row[0] for row in result]
            if not neighborhoods:
                raise ValueError(f"區 '{district}' 村里 '{village}' 不存在或無資料")
            
            return neighborhoods
        except Exception as e:
            logger.error(f"取得鄰列表失敗: {e}")
            raise
    
    def get_district_summary(self, district: str) -> AddressSummary:
        """查詢區的統計摘要"""
        try:
            result = self.db.execute(text("""
                SELECT 
                    COUNT(DISTINCT village) as village_count,
                    COUNT(DISTINCT CONCAT(village, '-', neighborhood)) as neighborhood_count,
                    COUNT(*) as address_count
                FROM addresses 
                WHERE district = :district
            """), {"district": district})
            
            stats = result.fetchone()
            if not stats or stats[2] == 0:
                raise ValueError(f"區 '{district}' 不存在")
            
            return AddressSummary(
                district=district,
                village_count=stats[0],
                neighborhood_count=stats[1],
                address_count=stats[2]
            )
        except Exception as e:
            logger.error(f"取得區統計摘要失敗: {e}")
            raise
    
    def get_village_summary(self, district: str, village: str) -> AddressSummary:
        """查詢村里的統計摘要"""
        try:
            result = self.db.execute(text("""
                SELECT 
                    COUNT(DISTINCT neighborhood) as neighborhood_count,
                    COUNT(*) as address_count
                FROM addresses 
                WHERE district = :district AND village = :village
            """), {"district": district, "village": village})
            
            stats = result.fetchone()
            if not stats or stats[1] == 0:
                raise ValueError(f"村里 '{district}{village}' 不存在")
            
            return AddressSummary(
                district=district,
                village=village,
                neighborhood_count=stats[0],
                address_count=stats[1]
            )
        except Exception as e:
            logger.error(f"取得村里統計摘要失敗: {e}")
            raise
    
    def get_neighborhood_details(self, district: str, village: str, neighborhood: int) -> NeighborhoodDetail:
        """查詢鄰的完整資料"""
        try:
            # 取得統計摘要
            summary_result = self.db.execute(text("""
                SELECT COUNT(*) as address_count
                FROM addresses 
                WHERE district = :district AND village = :village AND neighborhood = :neighborhood
            """), {"district": district, "village": village, "neighborhood": neighborhood})
            
            summary_stats = summary_result.fetchone()
            if not summary_stats or summary_stats[0] == 0:
                raise ValueError(f"鄰 '{district}{village}{neighborhood}鄰' 不存在")
            
            # 取得完整資料
            addresses_result = self.db.execute(text("""
                SELECT 
                    id, district, village, neighborhood, street, area, lane, alley, number,
                    x_coord, y_coord, full_address, created_at, updated_at
                FROM addresses 
                WHERE district = :district AND village = :village AND neighborhood = :neighborhood
                ORDER BY 
                    COALESCE(street, ''), 
                    COALESCE(lane, ''), 
                    COALESCE(alley, ''),
                    CASE 
                        WHEN number ~ '^[0-9]+' THEN CAST(REGEXP_REPLACE(number, '[^0-9].*$', '') AS INTEGER)
                        ELSE 999999
                    END,
                    number
            """), {"district": district, "village": village, "neighborhood": neighborhood})
            
            addresses = []
            for row in addresses_result:
                address_data = {
                    "id": row[0],
                    "district": row[1],
                    "village": row[2],
                    "neighborhood": row[3],
                    "street": row[4],
                    "area": row[5],
                    "lane": row[6],
                    "alley": row[7],
                    "number": row[8],
                    "x_coord": float(row[9]) if row[9] else None,
                    "y_coord": float(row[10]) if row[10] else None,
                    "full_address": row[11],
                    "created_at": row[12],
                    "updated_at": row[13]
                }
                addresses.append(address_data)
            
            summary = AddressSummary(
                district=district,
                village=village,
                neighborhood=neighborhood,
                address_count=summary_stats[0]
            )
            
            return NeighborhoodDetail(summary=summary, addresses=addresses)
        
        except Exception as e:
            logger.error(f"取得鄰詳細資料失敗: {e}")
            raise
    
    def search_addresses(self, params: SearchParams) -> Tuple[List[Dict], PaginationInfo]:
        """靈活搜尋地址"""
        try:
            # 建立查詢條件
            where_conditions = []
            query_params = {}
            
            if params.district:
                where_conditions.append("district = :district")
                query_params["district"] = params.district
                
            if params.village:
                where_conditions.append("village = :village")
                query_params["village"] = params.village
                
            if params.street:
                where_conditions.append("(street ILIKE :street OR area ILIKE :street)")
                query_params["street"] = f"%{params.street}%"
                
            if params.q:
                where_conditions.append("full_address ILIKE :q")
                query_params["q"] = f"%{params.q}%"
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # 計算總數
            count_query = text(f"""
                SELECT COUNT(*) 
                FROM addresses 
                WHERE {where_clause}
            """)
            total = self.db.execute(count_query, query_params).scalar()
            
            # 計算分頁
            offset = (params.page - 1) * params.per_page
            total_pages = math.ceil(total / params.per_page)
            
            # 查詢資料
            data_query = text(f"""
                SELECT 
                    id, district, village, neighborhood, street, area, lane, alley, number,
                    x_coord, y_coord, full_address, created_at, updated_at
                FROM addresses 
                WHERE {where_clause}
                ORDER BY district, village, neighborhood, id
                LIMIT :limit OFFSET :offset
            """)
            
            query_params.update({"limit": params.per_page, "offset": offset})
            result = self.db.execute(data_query, query_params)
            
            addresses = []
            for row in result:
                address_data = {
                    "id": row[0],
                    "district": row[1],
                    "village": row[2],
                    "neighborhood": row[3],
                    "street": row[4],
                    "area": row[5],
                    "lane": row[6],
                    "alley": row[7],
                    "number": row[8],
                    "x_coord": float(row[9]) if row[9] else None,
                    "y_coord": float(row[10]) if row[10] else None,
                    "full_address": row[11],
                    "created_at": row[12],
                    "updated_at": row[13]
                }
                addresses.append(address_data)
            
            pagination = PaginationInfo(
                page=params.page,
                per_page=params.per_page,
                total=total,
                pages=total_pages,
                has_prev=params.page > 1,
                has_next=params.page < total_pages
            )
            
            return addresses, pagination
        
        except Exception as e:
            logger.error(f"搜尋地址失敗: {e}")
            raise
    
    def search_nearby_addresses(self, params: GeoSearchParams) -> List[Dict]:
        """根據地理位置搜尋附近地址"""
        try:
            # 檢查 PostGIS 是否可用
            try:
                # 使用 PostGIS 空間查詢
                query = text("""
                    SELECT 
                        id, district, village, neighborhood, street, area, lane, alley, number,
                        x_coord, y_coord, full_address, created_at, updated_at,
                        ST_Distance(
                            ST_Transform(geom, 3826),  -- 轉換為適合台灣的投影座標系
                            ST_Transform(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), 3826)
                        ) as distance
                    FROM addresses 
                    WHERE geom IS NOT NULL
                    AND ST_DWithin(
                        ST_Transform(geom, 3826),
                        ST_Transform(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), 3826),
                        :radius
                    )
                    ORDER BY distance
                    LIMIT :limit
                """)
                
                result = self.db.execute(query, {
                    "lat": params.lat, 
                    "lng": params.lng, 
                    "radius": params.radius, 
                    "limit": params.limit
                })
                
            except Exception:
                # 如果 PostGIS 不可用，使用簡單的距離計算
                query = text("""
                    SELECT 
                        id, district, village, neighborhood, street, area, lane, alley, number,
                        x_coord, y_coord, full_address, created_at, updated_at,
                        (
                            6371000 * ACOS(
                                COS(RADIANS(:lat)) * COS(RADIANS(y_coord)) * 
                                COS(RADIANS(x_coord) - RADIANS(:lng)) + 
                                SIN(RADIANS(:lat)) * SIN(RADIANS(y_coord))
                            )
                        ) as distance
                    FROM addresses 
                    WHERE x_coord IS NOT NULL AND y_coord IS NOT NULL
                    AND (
                        6371000 * ACOS(
                            COS(RADIANS(:lat)) * COS(RADIANS(y_coord)) * 
                            COS(RADIANS(x_coord) - RADIANS(:lng)) + 
                            SIN(RADIANS(:lat)) * SIN(RADIANS(y_coord))
                        )
                    ) <= :radius
                    ORDER BY distance
                    LIMIT :limit
                """)
                
                result = self.db.execute(query, {
                    "lat": params.lat, 
                    "lng": params.lng, 
                    "radius": params.radius, 
                    "limit": params.limit
                })
            
            addresses = []
            for row in result:
                address_data = {
                    "id": row[0],
                    "district": row[1],
                    "village": row[2],
                    "neighborhood": row[3],
                    "street": row[4],
                    "area": row[5],
                    "lane": row[6],
                    "alley": row[7],
                    "number": row[8],
                    "x_coord": float(row[9]) if row[9] else None,
                    "y_coord": float(row[10]) if row[10] else None,
                    "full_address": row[11],
                    "created_at": row[12],
                    "updated_at": row[13],
                    "distance": round(float(row[14]), 2) if row[14] else None
                }
                addresses.append(address_data)
            
            return addresses
        
        except Exception as e:
            logger.error(f"地理位置搜尋失敗: {e}")
            raise
    
    def get_overview_stats(self) -> Dict[str, Any]:
        """取得系統總覽統計"""
        try:
            # 取得基本統計
            basic_stats = self.db.execute(text("""
                SELECT 
                    COUNT(*) as total_addresses,
                    COUNT(DISTINCT district) as total_districts,
                    COUNT(DISTINCT CONCAT(district, '|', village)) as total_villages,
                    COUNT(DISTINCT CONCAT(district, '|', village, '|', neighborhood)) as total_neighborhoods
                FROM addresses
            """)).fetchone()
            
            # 取得各區統計
            district_stats = self.db.execute(text("""
                SELECT 
                    district,
                    COUNT(DISTINCT village) as village_count,
                    COUNT(DISTINCT neighborhood) as neighborhood_count,
                    COUNT(*) as address_count
                FROM addresses
                GROUP BY district
                ORDER BY district
            """)).fetchall()
            
            districts = []
            for row in district_stats:
                districts.append({
                    "district": row[0],
                    "village_count": row[1],
                    "neighborhood_count": row[2],
                    "address_count": row[3]
                })
            
            return {
                "total_stats": {
                    "addresses": basic_stats[0],
                    "districts": basic_stats[1],
                    "villages": basic_stats[2],
                    "neighborhoods": basic_stats[3]
                },
                "district_breakdown": districts
            }
        
        except Exception as e:
            logger.error(f"取得統計總覽失敗: {e}")
            raise
    
    def export_addresses_csv(self, district: Optional[str] = None, 
                           village: Optional[str] = None, 
                           limit: int = 1000) -> Dict[str, Any]:
        """匯出地址資料為 CSV 格式"""
        try:
            # 建立查詢條件
            where_conditions = []
            params = {"limit": limit}
            
            if district:
                where_conditions.append("district = :district")
                params["district"] = district
                
            if village:
                where_conditions.append("village = :village")
                params["village"] = village
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # 查詢資料
            query = text(f"""
                SELECT 
                    district, village, neighborhood, street, area, lane, alley, number,
                    x_coord, y_coord, full_address
                FROM addresses 
                WHERE {where_clause}
                ORDER BY district, village, neighborhood, id
                LIMIT :limit
            """)
            
            result = self.db.execute(query, params)
            
            # 轉換為 CSV 格式的資料
            csv_data = []
            headers = ["區", "村里", "鄰", "街路段", "地區", "巷", "弄", "號", "橫座標", "縱座標", "完整地址"]
            
            for row in result:
                csv_data.append([
                    row[0],  # district
                    row[1],  # village
                    row[2],  # neighborhood
                    row[3] or "",  # street
                    row[4] or "",  # area
                    row[5] or "",  # lane
                    row[6] or "",  # alley
                    row[7] or "",  # number
                    row[8],  # x_coord
                    row[9],  # y_coord
                    row[10]  # full_address
                ])
            
            return {
                "headers": headers,
                "data": csv_data,
                "total_rows": len(csv_data),
                "filters": {
                    "district": district,
                    "village": village
                }
            }
        
        except Exception as e:
            logger.error(f"匯出 CSV 資料失敗: {e}")
            raise
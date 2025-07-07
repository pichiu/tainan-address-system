"""
地址查詢 API 端點
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import List, Optional
import math

from app.api.deps import get_db
from app.core.config import settings
from app.schemas.address import (
    Address, AddressSummary, NeighborhoodDetail, 
    APIResponse, PaginationInfo, SearchParams, GeoSearchParams
)
from app.services.address_service import AddressService

router = APIRouter()


@router.get("/districts", response_model=APIResponse)
async def get_districts(db: Session = Depends(get_db)):
    """取得所有區的列表"""
    try:
        service = AddressService(db)
        districts = service.get_districts()
        
        return APIResponse(
            success=True,
            data=districts,
            message=f"成功取得 {len(districts)} 個區"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得區列表失敗: {str(e)}")


@router.get("/villages", response_model=APIResponse)
async def get_villages(
    district: str = Query(..., description="區名"),
    db: Session = Depends(get_db)
):
    """取得指定區的所有村里"""
    try:
        service = AddressService(db)
        villages = service.get_villages(district)
        
        return APIResponse(
            success=True,
            data=villages,
            message=f"成功取得 {district} 的 {len(villages)} 個村里"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得村里列表失敗: {str(e)}")


@router.get("/neighborhoods", response_model=APIResponse)
async def get_neighborhoods(
    district: str = Query(..., description="區名"),
    village: str = Query(..., description="村里名"),
    db: Session = Depends(get_db)
):
    """取得指定區村里的所有鄰"""
    try:
        result = db.execute(text("""
            SELECT DISTINCT neighborhood 
            FROM addresses 
            WHERE district = :district AND village = :village 
            ORDER BY neighborhood
        """), {"district": district, "village": village})
        
        neighborhoods = [row[0] for row in result]
        
        if not neighborhoods:
            raise HTTPException(
                status_code=404, 
                detail=f"區 '{district}' 村里 '{village}' 不存在或無資料"
            )
        
        return APIResponse(
            success=True,
            data=neighborhoods,
            message=f"成功取得 {district}{village} 的 {len(neighborhoods)} 個鄰"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得鄰列表失敗: {str(e)}")


@router.get("/summary/district/{district}", response_model=APIResponse)
async def get_district_summary(district: str, db: Session = Depends(get_db)):
    """查詢區的統計摘要：有幾里、幾鄰、幾個門牌"""
    try:
        result = db.execute(text("""
            SELECT 
                COUNT(DISTINCT village) as village_count,
                COUNT(DISTINCT CONCAT(village, '-', neighborhood)) as neighborhood_count,
                COUNT(*) as address_count
            FROM addresses 
            WHERE district = :district
        """), {"district": district})
        
        stats = result.fetchone()
        
        if not stats or stats[2] == 0:
            raise HTTPException(status_code=404, detail=f"區 '{district}' 不存在")
        
        summary = AddressSummary(
            district=district,
            village_count=stats[0],
            neighborhood_count=stats[1],
            address_count=stats[2]
        )
        
        return APIResponse(
            success=True,
            data=summary.model_dump(),
            message=f"{district} 統計摘要"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得區統計摘要失敗: {str(e)}")


@router.get("/summary/village/{district}/{village}", response_model=APIResponse)
async def get_village_summary(
    district: str, 
    village: str, 
    db: Session = Depends(get_db)
):
    """查詢村里的統計摘要：有幾鄰、幾個門牌"""
    try:
        result = db.execute(text("""
            SELECT 
                COUNT(DISTINCT neighborhood) as neighborhood_count,
                COUNT(*) as address_count
            FROM addresses 
            WHERE district = :district AND village = :village
        """), {"district": district, "village": village})
        
        stats = result.fetchone()
        
        if not stats or stats[1] == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"村里 '{district}{village}' 不存在"
            )
        
        summary = AddressSummary(
            district=district,
            village=village,
            neighborhood_count=stats[0],
            address_count=stats[1]
        )
        
        return APIResponse(
            success=True,
            data=summary.model_dump(),
            message=f"{district}{village} 統計摘要"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得村里統計摘要失敗: {str(e)}")


@router.get("/details/neighborhood/{district}/{village}/{neighborhood}", response_model=APIResponse)
async def get_neighborhood_details(
    district: str,
    village: str, 
    neighborhood: int,
    db: Session = Depends(get_db)
):
    """查詢鄰的完整資料：統計摘要 + 完整資料表格"""
    try:
        # 取得統計摘要
        summary_result = db.execute(text("""
            SELECT COUNT(*) as address_count
            FROM addresses 
            WHERE district = :district AND village = :village AND neighborhood = :neighborhood
        """), {"district": district, "village": village, "neighborhood": neighborhood})
        
        summary_stats = summary_result.fetchone()
        
        if not summary_stats or summary_stats[0] == 0:
            raise HTTPException(
                status_code=404, 
                detail=f"鄰 '{district}{village}{neighborhood}鄰' 不存在"
            )
        
        # 取得完整資料
        addresses_result = db.execute(text("""
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
            address = Address(
                id=row[0],
                district=row[1],
                village=row[2],
                neighborhood=row[3],
                street=row[4],
                area=row[5],
                lane=row[6],
                alley=row[7],
                number=row[8],
                x_coord=float(row[9]) if row[9] else None,
                y_coord=float(row[10]) if row[10] else None,
                full_address=row[11],
                created_at=row[12],
                updated_at=row[13]
            )
            addresses.append(address)
        
        summary = AddressSummary(
            district=district,
            village=village,
            neighborhood=neighborhood,
            address_count=summary_stats[0]
        )
        
        detail = NeighborhoodDetail(
            summary=summary,
            addresses=addresses
        )
        
        return APIResponse(
            success=True,
            data=detail.model_dump(),
            message=f"{district}{village}{neighborhood}鄰 詳細資料"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得鄰詳細資料失敗: {str(e)}")


@router.get("/search", response_model=APIResponse)
async def search_addresses(
    q: Optional[str] = Query(None, description="搜尋關鍵字"),
    district: Optional[str] = Query(None, description="區名"),
    village: Optional[str] = Query(None, description="村里名"),
    street: Optional[str] = Query(None, description="街道關鍵字"),
    page: int = Query(1, description="頁碼", ge=1),
    per_page: int = Query(20, description="每頁筆數", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """靈活搜尋地址"""
    try:
        service = AddressService(db)
        search_params = SearchParams(
            q=q,
            district=district,
            village=village,
            street=street,
            page=page,
            per_page=per_page
        )
        
        addresses, pagination = service.search_addresses(search_params)
        
        return APIResponse(
            success=True,
            data=addresses,
            message=f"搜尋到 {pagination.total} 筆地址資料",
            pagination=pagination
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜尋地址失敗: {str(e)}")


@router.get("/geo/nearby", response_model=APIResponse)
async def search_nearby_addresses(
    lat: float = Query(..., description="緯度", ge=21.8, le=25.3),
    lng: float = Query(..., description="經度", ge=119.3, le=122.0),
    radius: float = Query(1000, description="搜尋半徑(公尺)", ge=10, le=10000),
    limit: int = Query(50, description="結果數量限制", ge=1, le=100),
    db: Session = Depends(get_db)
):
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
            
            result = db.execute(query, {
                "lat": lat, 
                "lng": lng, 
                "radius": radius, 
                "limit": limit
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
            
            result = db.execute(query, {
                "lat": lat, 
                "lng": lng, 
                "radius": radius, 
                "limit": limit
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
        
        return APIResponse(
            success=True,
            data=addresses,
            message=f"在半徑 {radius} 公尺內找到 {len(addresses)} 筆地址"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"地理位置搜尋失敗: {str(e)}")


@router.get("/stats/overview", response_model=APIResponse)
async def get_overview_stats(db: Session = Depends(get_db)):
    """取得系統總覽統計"""
    try:
        # 取得基本統計
        basic_stats = db.execute(text("""
            SELECT 
                COUNT(*) as total_addresses,
                COUNT(DISTINCT district) as total_districts,
                COUNT(DISTINCT CONCAT(district, '|', village)) as total_villages,
                COUNT(DISTINCT CONCAT(district, '|', village, '|', neighborhood)) as total_neighborhoods
            FROM addresses
        """)).fetchone()
        
        # 取得各區統計
        district_stats = db.execute(text("""
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
        
        overview = {
            "total_stats": {
                "addresses": basic_stats[0],
                "districts": basic_stats[1],
                "villages": basic_stats[2],
                "neighborhoods": basic_stats[3]
            },
            "district_breakdown": districts
        }
        
        return APIResponse(
            success=True,
            data=overview,
            message="系統統計總覽"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得統計總覽失敗: {str(e)}")


@router.get("/export/csv", response_model=APIResponse)
async def export_addresses_csv(
    district: Optional[str] = Query(None, description="區名"),
    village: Optional[str] = Query(None, description="村里名"),
    limit: int = Query(1000, description="匯出筆數限制", ge=1, le=10000),
    db: Session = Depends(get_db)
):
    """匯出地址資料為 CSV 格式的資料"""
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
        
        result = db.execute(query, params)
        
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
        
        export_data = {
            "headers": headers,
            "data": csv_data,
            "total_rows": len(csv_data),
            "filters": {
                "district": district,
                "village": village
            }
        }
        
        return APIResponse(
            success=True,
            data=export_data,
            message=f"成功匯出 {len(csv_data)} 筆地址資料"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匯出 CSV 資料失敗: {str(e)}")


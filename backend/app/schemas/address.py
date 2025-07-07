"""
API 回應模型 (Pydantic Schemas)
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Union
from datetime import datetime


class AddressBase(BaseModel):
    """地址基本模型"""
    district: str = Field(..., description="區", example="中西區")
    village: str = Field(..., description="村里", example="赤崁里")
    neighborhood: int = Field(..., description="鄰", example=1)
    street: Optional[str] = Field(None, description="街、路段", example="民族路二段")
    area: Optional[str] = Field(None, description="地區", example="")
    lane: Optional[str] = Field(None, description="巷", example="317巷")
    alley: Optional[str] = Field(None, description="弄", example="")
    number: Optional[str] = Field(None, description="號", example="2號")
    x_coord: Optional[float] = Field(None, description="橫座標 (經度)", example=120.206001)
    y_coord: Optional[float] = Field(None, description="縱座標 (緯度)", example=22.997564)


class AddressCreate(AddressBase):
    """建立地址模型"""
    pass


class AddressUpdate(AddressBase):
    """更新地址模型"""
    district: Optional[str] = None
    village: Optional[str] = None
    neighborhood: Optional[int] = None


class AddressInDB(AddressBase):
    """資料庫中的地址模型"""
    id: int
    full_address: str = Field(..., description="完整地址")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Address(AddressInDB):
    """完整地址模型"""
    pass


class AddressSummary(BaseModel):
    """地址統計摘要模型"""
    district: Optional[str] = Field(None, description="區")
    village: Optional[str] = Field(None, description="村里")
    neighborhood: Optional[int] = Field(None, description="鄰")
    village_count: Optional[int] = Field(None, description="村里數量")
    neighborhood_count: Optional[int] = Field(None, description="鄰數量")
    address_count: int = Field(..., description="地址數量")
    
    model_config = ConfigDict(from_attributes=True)


class NeighborhoodDetail(BaseModel):
    """鄰詳細資料模型"""
    summary: AddressSummary
    addresses: List[Address]


class SearchParams(BaseModel):
    """搜尋參數模型"""
    q: Optional[str] = Field(None, description="搜尋關鍵字")
    district: Optional[str] = Field(None, description="區")
    village: Optional[str] = Field(None, description="村里")
    street: Optional[str] = Field(None, description="街道")
    page: int = Field(1, description="頁碼", ge=1)
    per_page: int = Field(20, description="每頁筆數", ge=1, le=100)


class GeoSearchParams(BaseModel):
    """地理搜尋參數模型"""
    lat: float = Field(..., description="緯度", ge=21.8, le=25.3)
    lng: float = Field(..., description="經度", ge=119.3, le=122.0)
    radius: float = Field(1000, description="搜尋半徑 (公尺)", ge=10, le=10000)
    limit: int = Field(50, description="結果數量限制", ge=1, le=100)


class PaginationInfo(BaseModel):
    """分頁資訊模型"""
    page: int = Field(..., description="目前頁碼")
    per_page: int = Field(..., description="每頁筆數")
    total: int = Field(..., description="總筆數")
    pages: int = Field(..., description="總頁數")
    has_prev: bool = Field(..., description="是否有上一頁")
    has_next: bool = Field(..., description="是否有下一頁")


class APIResponse(BaseModel):
    """標準 API 回應模型"""
    success: bool = Field(..., description="是否成功")
    data: Optional[Union[dict, list, str, int]] = Field(None, description="回應資料")
    message: str = Field(..., description="回應訊息")
    pagination: Optional[PaginationInfo] = Field(None, description="分頁資訊")
    error: Optional[str] = Field(None, description="錯誤訊息")


class DistrictInfo(BaseModel):
    """區資訊模型"""
    name: str = Field(..., description="區名")
    village_count: int = Field(..., description="村里數量")
    address_count: int = Field(..., description="地址數量")


class VillageInfo(BaseModel):
    """村里資訊模型"""
    name: str = Field(..., description="村里名")
    district: str = Field(..., description="所屬區")
    neighborhood_count: int = Field(..., description="鄰數量")
    address_count: int = Field(..., description="地址數量")


class NeighborhoodInfo(BaseModel):
    """鄰資訊模型"""
    number: int = Field(..., description="鄰號")
    district: str = Field(..., description="所屬區")
    village: str = Field(..., description="所屬村里")
    address_count: int = Field(..., description="地址數量")


class LicenseInfo(BaseModel):
    """授權資訊模型"""
    license: str = Field(..., description="授權條款")
    source: str = Field(..., description="資料來源")
    year: str = Field(..., description="資料年份")
    dataset: str = Field(..., description="資料集名稱")
    attribution: str = Field(..., description="標示要求")
    license_url: str = Field(..., description="授權條款網址")
    terms: dict = Field(..., description="使用條件")


class DatabaseStats(BaseModel):
    """資料庫統計模型"""
    table_exists: bool = Field(..., description="資料表是否存在")
    total_addresses: int = Field(..., description="總地址數量")
    districts: int = Field(..., description="區數量")
    villages: int = Field(..., description="村里數量")
    neighborhoods: int = Field(..., description="鄰數量")
    last_updated: Optional[datetime] = Field(None, description="最後更新時間")


class HealthCheck(BaseModel):
    """健康檢查模型"""
    status: str = Field(..., description="服務狀態")
    database: bool = Field(..., description="資料庫連線狀態")
    version: str = Field(..., description="系統版本")
    timestamp: datetime = Field(..., description="檢查時間")
    database_stats: Optional[DatabaseStats] = Field(None, description="資料庫統計")


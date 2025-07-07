"""
地址資料模型
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Index
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.core.database import Base


class Address(Base):
    """地址資料表模型"""
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    district = Column(String(10), nullable=False, comment="區")
    village = Column(String(20), nullable=False, comment="村里")
    neighborhood = Column(Integer, nullable=False, comment="鄰")
    street = Column(String(100), comment="街、路段")
    area = Column(String(50), comment="地區")
    lane = Column(String(20), comment="巷")
    alley = Column(String(20), comment="弄")
    number = Column(String(20), comment="號")
    x_coord = Column(Numeric(10, 6), comment="橫座標")
    y_coord = Column(Numeric(10, 6), comment="縱座標")
    full_address = Column(Text, comment="完整地址")
    geom = Column(Geometry('POINT', srid=4326), comment="地理座標")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 複合索引
    __table_args__ = (
        Index('idx_district_village', 'district', 'village'),
        Index('idx_district_village_neighborhood', 'district', 'village', 'neighborhood'),
        Index('idx_coordinates', 'x_coord', 'y_coord'),
    )
    
    def __repr__(self):
        return f"<Address(id={self.id}, district={self.district}, village={self.village}, neighborhood={self.neighborhood})>"
    
    @property
    def location_name(self) -> str:
        """取得位置名稱"""
        return f"{self.district}{self.village}{self.neighborhood}鄰"
    
    @property
    def coordinates(self) -> tuple:
        """取得座標 (經度, 緯度)"""
        if self.x_coord and self.y_coord:
            return (float(self.x_coord), float(self.y_coord))
        return None


class AddressStats(Base):
    """地址統計快取表模型"""
    __tablename__ = "address_stats"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    level = Column(String(20), nullable=False, comment="層級: district, village, neighborhood")
    district = Column(String(10), comment="區")
    village = Column(String(20), comment="村里")
    neighborhood = Column(Integer, comment="鄰")
    address_count = Column(Integer, nullable=False, default=0, comment="地址數量")
    village_count = Column(Integer, default=0, comment="村里數量")
    neighborhood_count = Column(Integer, default=0, comment="鄰數量")
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 唯一約束
    __table_args__ = (
        Index('idx_stats_unique', 'level', 'district', 'village', 'neighborhood', unique=True),
        Index('idx_stats_level', 'level'),
        Index('idx_stats_district', 'district'),
    )
    
    def __repr__(self):
        return f"<AddressStats(level={self.level}, district={self.district}, village={self.village}, address_count={self.address_count})>"


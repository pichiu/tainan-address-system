/**
 * TypeScript 類型定義
 */

// 基本地址介面
export interface Address {
  id: number;
  district: string;
  village: string;
  neighborhood: number;
  street?: string;
  area?: string;
  lane?: string;
  alley?: string;
  number?: string;
  x_coord?: number;
  y_coord?: number;
  full_address: string;
  created_at: string;
  updated_at: string;
  distance?: number; // 用於地理搜尋
}

// 地址統計摘要
export interface AddressSummary {
  district?: string;
  village?: string;
  neighborhood?: number;
  village_count?: number;
  neighborhood_count?: number;
  address_count: number;
}

// 鄰詳細資料
export interface NeighborhoodDetail {
  summary: AddressSummary;
  addresses: Address[];
}

// 搜尋參數
export interface SearchParams {
  q?: string;
  district?: string;
  village?: string;
  street?: string;
  page?: number;
  per_page?: number;
}

// 地理搜尋參數
export interface GeoSearchParams {
  lat: number;
  lng: number;
  radius: number;
  limit?: number;
}

// 分頁資訊
export interface PaginationInfo {
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_prev: boolean;
  has_next: boolean;
}

// API 回應格式
export interface APIResponse<T = any> {
  success: boolean;
  data: T;
  message: string;
  pagination?: PaginationInfo;
  error?: string;
}

// 區資訊
export interface DistrictInfo {
  name: string;
  village_count: number;
  address_count: number;
}

// 村里資訊
export interface VillageInfo {
  name: string;
  district: string;
  neighborhood_count: number;
  address_count: number;
}

// 鄰資訊
export interface NeighborhoodInfo {
  number: number;
  district: string;
  village: string;
  address_count: number;
}

// 授權資訊
export interface LicenseInfo {
  license: string;
  source: string;
  year: string;
  dataset: string;
  attribution: string;
  license_url: string;
  terms: {
    usage: string;
    attribution_required: boolean;
    commercial_use: boolean;
    modification: boolean;
    redistribution: boolean;
  };
}

// 資料庫統計
export interface DatabaseStats {
  table_exists: boolean;
  total_addresses: number;
  districts: number;
  villages: number;
  neighborhoods: number;
  last_updated?: string;
}

// 健康檢查
export interface HealthCheck {
  status: string;
  database: boolean;
  version: string;
  timestamp: string;
  database_stats?: DatabaseStats;
}

// 地圖相關
export interface MapViewport {
  center: [number, number]; // [lat, lng]
  zoom: number;
}

export interface MapMarker {
  id: string;
  position: [number, number]; // [lat, lng]
  popup?: string;
  address?: Address;
}

// 元件 Props 類型
export interface AddressTableProps {
  addresses: Address[];
  onAddressSelect?: (address: Address) => void;
  showPagination?: boolean;
  loading?: boolean;
}

export interface MapViewerProps {
  addresses: Address[];
  center?: [number, number];
  zoom?: number;
  onAddressClick?: (address: Address) => void;
  height?: string | number;
}

export interface SummaryCardProps {
  summary: AddressSummary;
  sx?: any;
}

// 搜尋結果類型
export interface SearchResult {
  addresses: Address[];
  pagination: PaginationInfo;
  total: number;
}

// 匯出資料類型
export interface ExportData {
  headers: string[];
  data: string[][];
  total_rows: number;
  filters: {
    district?: string;
    village?: string;
  };
}

// 統計總覽
export interface OverviewStats {
  total_stats: {
    addresses: number;
    districts: number;
    villages: number;
    neighborhoods: number;
  };
  district_breakdown: Array<{
    district: string;
    village_count: number;
    neighborhood_count: number;
    address_count: number;
  }>;
}

// 錯誤類型
export interface APIError {
  message: string;
  status?: number;
  code?: string;
}

// 應用狀態類型
export interface AppState {
  selectedDistrict: string;
  selectedVillage: string;
  selectedNeighborhood: string;
  searchKeyword: string;
  showMap: boolean;
  mapCenter: [number, number];
  mapZoom: number;
}

// 設定類型
export interface AppConfig {
  apiBaseUrl: string;
  mapDefaultCenter: [number, number];
  mapDefaultZoom: number;
  mapTileUrl: string;
  mapAttribution: string;
  defaultPageSize: number;
  maxPageSize: number;
}

// 使用者偏好設定
export interface UserPreferences {
  theme: 'light' | 'dark';
  language: 'zh-TW' | 'en';
  mapStyle: 'osm' | 'satellite';
  showCoordinates: boolean;
  autoRefresh: boolean;
}

// Form 相關類型
export interface SearchFormData {
  district: string;
  village: string;
  neighborhood: string;
  keyword: string;
}

export interface FilterOptions {
  districts: string[];
  villages: string[];
  neighborhoods: number[];
}

// 快取類型
export interface CacheItem<T> {
  data: T;
  timestamp: number;
  expiry: number;
}

// 事件類型
export interface AddressSelectEvent {
  address: Address;
  source: 'table' | 'map' | 'search';
}

export interface MapEvent {
  type: 'click' | 'move' | 'zoom';
  position?: [number, number];
  zoom?: number;
  address?: Address;
}

// 分析和統計類型
export interface DistrictStats {
  district: string;
  total_addresses: number;
  villages: VillageStats[];
  density: number; // 每平方公里地址數
  coverage: number; // 覆蓋率百分比
}

export interface VillageStats {
  village: string;
  district: string;
  total_addresses: number;
  neighborhoods: NeighborhoodStats[];
  area?: number; // 面積（平方公里）
}

export interface NeighborhoodStats {
  neighborhood: number;
  village: string;
  district: string;
  total_addresses: number;
  coordinates?: {
    center: [number, number];
    bounds: [[number, number], [number, number]];
  };
}


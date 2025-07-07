/**
 * API 客戶端服務
 */
import axios, { AxiosResponse } from 'axios';
import type {
  APIResponse,
  AddressSummary,
  NeighborhoodDetail,
  Address,
  SearchParams,
  GeoSearchParams,
  DatabaseStats,
  LicenseInfo
} from './types';

// API 基本設定
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 請求攔截器
apiClient.interceptors.request.use(
  (config) => {
    // 可在此添加認證 token 等
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// 回應攔截器
apiClient.interceptors.response.use(
  (response: AxiosResponse<APIResponse>) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    
    // 檢查 API 回應格式
    if (response.data && !response.data.success) {
      throw new Error(response.data.message || 'API 回應失敗');
    }
    
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    // 處理不同類型的錯誤
    if (error.response) {
      // 伺服器回應錯誤
      const message = error.response.data?.message || `HTTP ${error.response.status} 錯誤`;
      throw new Error(message);
    } else if (error.request) {
      // 網路錯誤
      throw new Error('網路連線失敗，請檢查網路狀態');
    } else {
      // 其他錯誤
      throw new Error(error.message || '未知錯誤');
    }
  }
);

// API 服務類別
export class AddressAPI {
  /**
   * 取得所有區
   */
  async getDistricts(): Promise<string[]> {
    const response = await apiClient.get<APIResponse>('/districts');
    return response.data.data as string[];
  }

  /**
   * 取得指定區的村里
   */
  async getVillages(district: string): Promise<string[]> {
    const response = await apiClient.get<APIResponse>('/villages', {
      params: { district }
    });
    return response.data.data as string[];
  }

  /**
   * 取得指定區村里的鄰
   */
  async getNeighborhoods(district: string, village: string): Promise<number[]> {
    const response = await apiClient.get<APIResponse>('/neighborhoods', {
      params: { district, village }
    });
    return response.data.data as number[];
  }

  /**
   * 取得區統計摘要
   */
  async getDistrictSummary(district: string): Promise<AddressSummary> {
    const response = await apiClient.get<APIResponse>(`/summary/district/${encodeURIComponent(district)}`);
    return response.data.data as AddressSummary;
  }

  /**
   * 取得村里統計摘要
   */
  async getVillageSummary(district: string, village: string): Promise<AddressSummary> {
    const response = await apiClient.get<APIResponse>(
      `/summary/village/${encodeURIComponent(district)}/${encodeURIComponent(village)}`
    );
    return response.data.data as AddressSummary;
  }

  /**
   * 取得鄰詳細資料
   */
  async getNeighborhoodDetails(
    district: string, 
    village: string, 
    neighborhood: number
  ): Promise<NeighborhoodDetail> {
    const response = await apiClient.get<APIResponse>(
      `/details/neighborhood/${encodeURIComponent(district)}/${encodeURIComponent(village)}/${neighborhood}`
    );
    return response.data.data as NeighborhoodDetail;
  }

  /**
   * 搜尋地址
   */
  async searchAddresses(params: SearchParams): Promise<APIResponse> {
    const response = await apiClient.get<APIResponse>('/search', {
      params: {
        q: params.q,
        district: params.district,
        village: params.village,
        street: params.street,
        page: params.page || 1,
        per_page: params.per_page || 20
      }
    });
    return response.data;
  }

  /**
   * 地理位置搜尋
   */
  async searchNearby(params: GeoSearchParams): Promise<Address[]> {
    const response = await apiClient.get<APIResponse>('/geo/nearby', {
      params: {
        lat: params.lat,
        lng: params.lng,
        radius: params.radius,
        limit: params.limit
      }
    });
    return response.data.data as Address[];
  }

  /**
   * 取得系統統計總覽
   */
  async getOverviewStats(): Promise<any> {
    const response = await apiClient.get<APIResponse>('/stats/overview');
    return response.data.data;
  }

  /**
   * 匯出 CSV 資料
   */
  async exportCSV(district?: string, village?: string, limit: number = 1000): Promise<any> {
    const response = await apiClient.get<APIResponse>('/export/csv', {
      params: { district, village, limit }
    });
    return response.data.data;
  }

  /**
   * 取得授權資訊
   */
  async getLicense(): Promise<LicenseInfo> {
    const response = await apiClient.get<APIResponse>('/license');
    return response.data.data as LicenseInfo;
  }

  /**
   * 健康檢查
   */
  async healthCheck(): Promise<any> {
    const response = await apiClient.get<APIResponse>('/health/');
    return response.data.data;
  }

  /**
   * 詳細健康檢查
   */
  async detailedHealthCheck(): Promise<any> {
    const response = await apiClient.get<APIResponse>('/health/detailed');
    return response.data.data;
  }
}

// 建立 API 實例
export const addressAPI = new AddressAPI();

// 匯出常用的 API 方法
export const {
  getDistricts,
  getVillages,
  getNeighborhoods,
  getDistrictSummary,
  getVillageSummary,
  getNeighborhoodDetails,
  searchAddresses,
  searchNearby,
  getOverviewStats,
  exportCSV,
  getLicense,
  healthCheck,
  detailedHealthCheck
} = addressAPI;


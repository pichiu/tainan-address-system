/**
 * 地址搜尋相關的 React Hook
 */
import { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { addressAPI } from '../services/api';
import type { 
  AddressSummary, 
  NeighborhoodDetail, 
  Address,
  SearchParams 
} from '../services/types';

interface UseAddressSearchReturn {
  // 資料狀態
  districts: string[];
  villages: string[];
  neighborhoods: number[];
  summary: AddressSummary | null;
  details: NeighborhoodDetail | null;
  searchResults: Address[] | null;
  
  // 載入狀態
  loading: boolean;
  error: string | null;
  
  // 操作方法
  loadVillages: (district: string) => void;
  loadNeighborhoods: (district: string, village: string) => void;
  loadDistrictSummary: (district: string) => void;
  loadVillageSummary: (district: string, village: string) => void;
  loadNeighborhoodDetails: (district: string, village: string, neighborhood: number) => void;
  searchAddresses: (params: SearchParams) => void;
  clearResults: () => void;
}

export const useAddressSearch = (): UseAddressSearchReturn => {
  // 本地狀態
  const [villages, setVillages] = useState<string[]>([]);
  const [neighborhoods, setNeighborhoods] = useState<number[]>([]);
  const [summary, setSummary] = useState<AddressSummary | null>(null);
  const [details, setDetails] = useState<NeighborhoodDetail | null>(null);
  const [searchResults, setSearchResults] = useState<Address[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  // 取得所有區
  const { data: districts = [], isLoading: districtsLoading } = useQuery({
    queryKey: ['districts'],
    queryFn: addressAPI.getDistricts,
    staleTime: 1000 * 60 * 60, // 1小時
  });

  // 載入村里
  const villagesMutation = useMutation({
    mutationFn: ({ district }: { district: string }) => 
      addressAPI.getVillages(district),
    onSuccess: (data) => {
      setVillages(data);
      setError(null);
    },
    onError: (error: any) => {
      setError(error.message || '載入村里失敗');
      setVillages([]);
    }
  });

  // 載入鄰
  const neighborhoodsMutation = useMutation({
    mutationFn: ({ district, village }: { district: string; village: string }) =>
      addressAPI.getNeighborhoods(district, village),
    onSuccess: (data) => {
      setNeighborhoods(data);
      setError(null);
    },
    onError: (error: any) => {
      setError(error.message || '載入鄰失敗');
      setNeighborhoods([]);
    }
  });

  // 載入區統計
  const districtSummaryMutation = useMutation({
    mutationFn: ({ district }: { district: string }) =>
      addressAPI.getDistrictSummary(district),
    onSuccess: (data) => {
      setSummary(data);
      setDetails(null);
      setSearchResults(null);
      setError(null);
    },
    onError: (error: any) => {
      setError(error.message || '載入區統計失敗');
      setSummary(null);
    }
  });

  // 載入村里統計
  const villageSummaryMutation = useMutation({
    mutationFn: ({ district, village }: { district: string; village: string }) =>
      addressAPI.getVillageSummary(district, village),
    onSuccess: (data) => {
      setSummary(data);
      setDetails(null);
      setSearchResults(null);
      setError(null);
    },
    onError: (error: any) => {
      setError(error.message || '載入村里統計失敗');
      setSummary(null);
    }
  });

  // 載入鄰詳細資料
  const neighborhoodDetailsMutation = useMutation({
    mutationFn: ({ 
      district, 
      village, 
      neighborhood 
    }: { 
      district: string; 
      village: string; 
      neighborhood: number; 
    }) => addressAPI.getNeighborhoodDetails(district, village, neighborhood),
    onSuccess: (data) => {
      setDetails(data);
      setSummary(data.summary);
      setSearchResults(null);
      setError(null);
    },
    onError: (error: any) => {
      setError(error.message || '載入鄰詳細資料失敗');
      setDetails(null);
    }
  });

  // 搜尋地址
  const searchMutation = useMutation({
    mutationFn: (params: SearchParams) => addressAPI.searchAddresses(params),
    onSuccess: (data) => {
      setSearchResults(data.data);
      setSummary(null);
      setDetails(null);
      setError(null);
    },
    onError: (error: any) => {
      setError(error.message || '搜尋失敗');
      setSearchResults(null);
    }
  });

  // 計算載入狀態
  const loading = 
    districtsLoading ||
    villagesMutation.isPending ||
    neighborhoodsMutation.isPending ||
    districtSummaryMutation.isPending ||
    villageSummaryMutation.isPending ||
    neighborhoodDetailsMutation.isPending ||
    searchMutation.isPending;

  // 公開方法
  const loadVillages = (district: string) => {
    villagesMutation.mutate({ district });
  };

  const loadNeighborhoods = (district: string, village: string) => {
    neighborhoodsMutation.mutate({ district, village });
  };

  const loadDistrictSummary = (district: string) => {
    districtSummaryMutation.mutate({ district });
  };

  const loadVillageSummary = (district: string, village: string) => {
    villageSummaryMutation.mutate({ district, village });
  };

  const loadNeighborhoodDetails = (
    district: string, 
    village: string, 
    neighborhood: number
  ) => {
    neighborhoodDetailsMutation.mutate({ district, village, neighborhood });
  };

  const searchAddresses = (params: SearchParams) => {
    searchMutation.mutate(params);
  };

  const clearResults = () => {
    setSummary(null);
    setDetails(null);
    setSearchResults(null);
    setError(null);
  };

  // 清除錯誤當有新的成功操作時
  useEffect(() => {
    if (!loading && error) {
      const timer = setTimeout(() => {
        setError(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [loading, error]);

  return {
    // 資料狀態
    districts,
    villages,
    neighborhoods,
    summary,
    details,
    searchResults,
    
    // 載入狀態
    loading,
    error,
    
    // 操作方法
    loadVillages,
    loadNeighborhoods,
    loadDistrictSummary,
    loadVillageSummary,
    loadNeighborhoodDetails,
    searchAddresses,
    clearResults,
  };
};


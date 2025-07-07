/**
 * 地址搜尋主元件
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  Paper,
  Divider,
  Button,
  TextField
} from '@mui/material';
import {
  Search as SearchIcon,
  LocationOn as LocationIcon,
  Business as BusinessIcon,
  Home as HomeIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import { useAddressSearch } from '../hooks/useAddressSearch';
import { AddressTable } from './AddressTable';
import { MapViewer } from './MapViewer';
import { SummaryCard } from './SummaryCard';

interface AddressSearchProps {
  onAddressSelect?: (address: any) => void;
}

export const AddressSearch: React.FC<AddressSearchProps> = ({ 
  onAddressSelect 
}) => {
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [selectedVillage, setSelectedVillage] = useState('');
  const [selectedNeighborhood, setSelectedNeighborhood] = useState('');
  const [searchKeyword, setSearchKeyword] = useState('');
  const [showMap, setShowMap] = useState(false);

  const {
    districts,
    villages,
    neighborhoods,
    summary,
    details,
    searchResults,
    loading,
    error,
    loadVillages,
    loadNeighborhoods,
    loadDistrictSummary,
    loadVillageSummary,
    loadNeighborhoodDetails,
    searchAddresses,
    clearResults
  } = useAddressSearch();

  // 處理區選擇
  const handleDistrictChange = (district: string) => {
    setSelectedDistrict(district);
    setSelectedVillage('');
    setSelectedNeighborhood('');
    clearResults();
    
    if (district) {
      loadVillages(district);
      loadDistrictSummary(district);
    }
  };

  // 處理村里選擇
  const handleVillageChange = (village: string) => {
    setSelectedVillage(village);
    setSelectedNeighborhood('');
    clearResults();
    
    if (village && selectedDistrict) {
      loadNeighborhoods(selectedDistrict, village);
      loadVillageSummary(selectedDistrict, village);
    }
  };

  // 處理鄰選擇
  const handleNeighborhoodChange = (neighborhood: string) => {
    setSelectedNeighborhood(neighborhood);
    
    if (neighborhood && selectedDistrict && selectedVillage) {
      loadNeighborhoodDetails(
        selectedDistrict, 
        selectedVillage, 
        parseInt(neighborhood)
      );
    }
  };

  // 處理關鍵字搜尋
  const handleSearch = () => {
    if (searchKeyword.trim()) {
      searchAddresses({
        q: searchKeyword,
        district: selectedDistrict || undefined,
        village: selectedVillage || undefined
      });
    }
  };

  // 清除所有選擇
  const handleClearAll = () => {
    setSelectedDistrict('');
    setSelectedVillage('');
    setSelectedNeighborhood('');
    setSearchKeyword('');
    clearResults();
  };

  // 取得目前選擇的麵包屑
  const getBreadcrumbs = () => {
    const crumbs = [];
    if (selectedDistrict) {
      crumbs.push({
        label: selectedDistrict,
        icon: <BusinessIcon fontSize="small" />
      });
    }
    if (selectedVillage) {
      crumbs.push({
        label: selectedVillage,
        icon: <LocationIcon fontSize="small" />
      });
    }
    if (selectedNeighborhood) {
      crumbs.push({
        label: `${selectedNeighborhood}鄰`,
        icon: <HomeIcon fontSize="small" />
      });
    }
    return crumbs;
  };

  const breadcrumbs = getBreadcrumbs();

  return (
    <Box sx={{ width: '100%' }}>
      {/* 搜尋控制面板 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            地址查詢
          </Typography>
          
          {/* 行政區選擇 */}
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>區</InputLabel>
                <Select
                  value={selectedDistrict}
                  label="區"
                  onChange={(e) => handleDistrictChange(e.target.value)}
                  disabled={loading}
                >
                  <MenuItem value="">
                    <em>請選擇區</em>
                  </MenuItem>
                  {districts.map((district) => (
                    <MenuItem key={district} value={district}>
                      {district}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>村里</InputLabel>
                <Select
                  value={selectedVillage}
                  label="村里"
                  onChange={(e) => handleVillageChange(e.target.value)}
                  disabled={loading || !selectedDistrict}
                >
                  <MenuItem value="">
                    <em>請選擇村里</em>
                  </MenuItem>
                  {villages.map((village) => (
                    <MenuItem key={village} value={village}>
                      {village}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>鄰</InputLabel>
                <Select
                  value={selectedNeighborhood}
                  label="鄰"
                  onChange={(e) => handleNeighborhoodChange(e.target.value)}
                  disabled={loading || !selectedVillage}
                >
                  <MenuItem value="">
                    <em>請選擇鄰</em>
                  </MenuItem>
                  {neighborhoods.map((neighborhood) => (
                    <MenuItem key={neighborhood} value={neighborhood.toString()}>
                      {neighborhood}鄰
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {/* 關鍵字搜尋 */}
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={8}>
              <TextField
                fullWidth
                label="搜尋關鍵字"
                placeholder="輸入街道、門牌號碼等關鍵字"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                disabled={loading}
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={handleSearch}
                disabled={loading || !searchKeyword.trim()}
                sx={{ height: 56 }}
              >
                搜尋
              </Button>
            </Grid>
            <Grid item xs={12} sm={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<ClearIcon />}
                onClick={handleClearAll}
                disabled={loading}
                sx={{ height: 56 }}
              >
                清除
              </Button>
            </Grid>
          </Grid>

          {/* 麵包屑導航 */}
          {breadcrumbs.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                目前位置：
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {breadcrumbs.map((crumb, index) => (
                  <Chip
                    key={index}
                    icon={crumb.icon}
                    label={crumb.label}
                    size="small"
                    variant="outlined"
                    color="primary"
                  />
                ))}
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* 載入指示器 */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
          <CircularProgress />
        </Box>
      )}

      {/* 錯誤訊息 */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* 統計摘要 */}
      {summary && (
        <SummaryCard summary={summary} sx={{ mb: 3 }} />
      )}

      {/* 詳細資料和地圖 */}
      {(details || searchResults) && (
        <Card>
          <CardContent>
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              mb: 2 
            }}>
              <Typography variant="h6">
                {details ? 
                  `${selectedDistrict}${selectedVillage}${selectedNeighborhood}鄰 詳細資料` :
                  '搜尋結果'
                }
              </Typography>
              <Button
                variant="outlined"
                onClick={() => setShowMap(!showMap)}
                startIcon={<LocationIcon />}
              >
                {showMap ? '隱藏地圖' : '顯示地圖'}
              </Button>
            </Box>

            {/* 地圖顯示 */}
            {showMap && (
              <Box sx={{ mb: 3 }}>
                <MapViewer 
                  addresses={details?.addresses || searchResults || []}
                  onAddressClick={onAddressSelect}
                />
              </Box>
            )}

            <Divider sx={{ mb: 2 }} />

            {/* 地址表格 */}
            <AddressTable
              addresses={details?.addresses || searchResults || []}
              onAddressSelect={onAddressSelect}
              showPagination={!!searchResults}
            />
          </CardContent>
        </Card>
      )}

      {/* 無資料提示 */}
      {!loading && !error && !summary && !details && !searchResults && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            請選擇行政區域或輸入關鍵字開始查詢
          </Typography>
        </Paper>
      )}
    </Box>
  );
};


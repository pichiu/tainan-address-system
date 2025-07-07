/**
 * 統計摘要卡片元件
 */
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Box,
  Chip,
  Divider,
  Paper
} from '@mui/material';
import {
  LocationCity as DistrictIcon,
  LocationOn as VillageIcon,
  Home as NeighborhoodIcon,
  ListAlt as AddressIcon
} from '@mui/icons-material';

interface SummaryData {
  district?: string;
  village?: string;
  neighborhood?: number;
  village_count?: number;
  neighborhood_count?: number;
  address_count: number;
}

interface SummaryCardProps {
  summary: SummaryData;
  sx?: object;
}

export const SummaryCard: React.FC<SummaryCardProps> = ({ summary, sx }) => {
  const formatNumber = (num: number): string => {
    return num.toLocaleString();
  };

  const getTitle = (): string => {
    if (summary.neighborhood) {
      return `${summary.district}${summary.village}${summary.neighborhood}鄰`;
    } else if (summary.village) {
      return `${summary.district}${summary.village}`;
    } else if (summary.district) {
      return summary.district;
    }
    return '統計摘要';
  };

  const getSubtitle = (): string => {
    if (summary.neighborhood) {
      return '鄰級統計';
    } else if (summary.village) {
      return '村里級統計';
    } else if (summary.district) {
      return '區級統計';
    }
    return '總體統計';
  };

  return (
    <Card sx={{ ...sx }}>
      <CardContent>
        {/* 標題區域 */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" component="div" gutterBottom>
            {getTitle()}
          </Typography>
          <Chip 
            label={getSubtitle()}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* 統計數據 */}
        <Grid container spacing={2}>
          {/* 地址數量 - 永遠顯示 */}
          <Grid item xs={12} sm={6} md={3}>
            <Paper 
              sx={{ 
                p: 2, 
                textAlign: 'center',
                bgcolor: 'primary.main',
                color: 'primary.contrastText'
              }}
            >
              <AddressIcon sx={{ fontSize: 32, mb: 1 }} />
              <Typography variant="h4" component="div">
                {formatNumber(summary.address_count)}
              </Typography>
              <Typography variant="body2">
                地址數量
              </Typography>
            </Paper>
          </Grid>

          {/* 村里數量 - 僅在區級統計時顯示 */}
          {summary.village_count !== undefined && (
            <Grid item xs={12} sm={6} md={3}>
              <Paper 
                sx={{ 
                  p: 2, 
                  textAlign: 'center',
                  bgcolor: 'secondary.main',
                  color: 'secondary.contrastText'
                }}
              >
                <VillageIcon sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h4" component="div">
                  {formatNumber(summary.village_count)}
                </Typography>
                <Typography variant="body2">
                  村里數量
                </Typography>
              </Paper>
            </Grid>
          )}

          {/* 鄰數量 - 在區級和村里級統計時顯示 */}
          {summary.neighborhood_count !== undefined && (
            <Grid item xs={12} sm={6} md={3}>
              <Paper 
                sx={{ 
                  p: 2, 
                  textAlign: 'center',
                  bgcolor: 'success.main',
                  color: 'success.contrastText'
                }}
              >
                <NeighborhoodIcon sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="h4" component="div">
                  {formatNumber(summary.neighborhood_count)}
                </Typography>
                <Typography variant="body2">
                  鄰數量
                </Typography>
              </Paper>
            </Grid>
          )}

          {/* 密度統計 */}
          <Grid item xs={12} sm={6} md={3}>
            <Paper 
              sx={{ 
                p: 2, 
                textAlign: 'center',
                bgcolor: 'info.main',
                color: 'info.contrastText'
              }}
            >
              <DistrictIcon sx={{ fontSize: 32, mb: 1 }} />
              <Typography variant="h4" component="div">
                {summary.neighborhood_count 
                  ? Math.round(summary.address_count / summary.neighborhood_count)
                  : summary.village_count
                  ? Math.round(summary.address_count / summary.village_count)
                  : summary.address_count
                }
              </Typography>
              <Typography variant="body2">
                {summary.neighborhood_count 
                  ? '平均每鄰'
                  : summary.village_count
                  ? '平均每村里'
                  : '總計'
                }
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* 詳細說明 */}
        <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            <strong>統計說明：</strong>
            {summary.neighborhood 
              ? `${getTitle()}的完整地址清單，包含 ${formatNumber(summary.address_count)} 筆門牌資料。`
              : summary.village
              ? `${getTitle()}包含 ${formatNumber(summary.neighborhood_count!)} 個鄰，共 ${formatNumber(summary.address_count)} 筆門牌資料。`
              : summary.district
              ? `${getTitle()}包含 ${formatNumber(summary.village_count!)} 個村里、${formatNumber(summary.neighborhood_count!)} 個鄰，共 ${formatNumber(summary.address_count)} 筆門牌資料。`
              : `總計 ${formatNumber(summary.address_count)} 筆門牌資料。`
            }
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};
/**
 * 地址表格元件
 */
import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Box,
  Typography,
  Button
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  Visibility as ViewIcon,
  GetApp as ExportIcon
} from '@mui/icons-material';

interface Address {
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
}

interface AddressTableProps {
  addresses: Address[];
  onAddressSelect?: (address: Address) => void;
  showPagination?: boolean;
  onPageChange?: (page: number) => void;
  onRowsPerPageChange?: (rowsPerPage: number) => void;
  totalCount?: number;
  currentPage?: number;
  rowsPerPage?: number;
}

export const AddressTable: React.FC<AddressTableProps> = ({
  addresses,
  onAddressSelect,
  showPagination = true,
  onPageChange,
  onRowsPerPageChange,
  totalCount = addresses.length,
  currentPage = 0,
  rowsPerPage = 10
}) => {
  const [page, setPage] = useState(currentPage);
  const [rowsPerPageState, setRowsPerPageState] = useState(rowsPerPage);

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
    onPageChange?.(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newRowsPerPage = parseInt(event.target.value, 10);
    setRowsPerPageState(newRowsPerPage);
    setPage(0);
    onRowsPerPageChange?.(newRowsPerPage);
  };

  const handleAddressClick = (address: Address) => {
    onAddressSelect?.(address);
  };

  const buildFullAddress = (address: Address): string => {
    const parts = [
      address.district,
      address.village,
      `${address.neighborhood}鄰`,
      address.street,
      address.area,
      address.lane,
      address.alley,
      address.number
    ];
    return parts.filter(Boolean).join('');
  };

  const exportToCsv = () => {
    const headers = ['區', '村里', '鄰', '街道', '地區', '巷', '弄', '號', '經度', '緯度', '完整地址'];
    const csvData = addresses.map(addr => [
      addr.district,
      addr.village,
      addr.neighborhood,
      addr.street || '',
      addr.area || '',
      addr.lane || '',
      addr.alley || '',
      addr.number || '',
      addr.x_coord || '',
      addr.y_coord || '',
      addr.full_address
    ]);

    const csvContent = [headers, ...csvData]
      .map(row => row.map(field => `"${field}"`).join(','))
      .join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `tainan_addresses_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (addresses.length === 0) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography color="text.secondary">
          沒有找到地址資料
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      {/* 工具列 */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        mb: 2 
      }}>
        <Typography variant="h6" component="div">
          地址清單 ({totalCount.toLocaleString()} 筆)
        </Typography>
        <Button
          variant="outlined"
          startIcon={<ExportIcon />}
          onClick={exportToCsv}
          size="small"
        >
          匯出 CSV
        </Button>
      </Box>

      {/* 表格 */}
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="地址表格">
          <TableHead>
            <TableRow>
              <TableCell>區域</TableCell>
              <TableCell>詳細地址</TableCell>
              <TableCell>座標</TableCell>
              <TableCell align="center">操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {addresses.map((address) => (
              <TableRow 
                key={address.id}
                hover
                sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
              >
                <TableCell>
                  <Box>
                    <Chip 
                      label={address.district}
                      size="small"
                      color="primary"
                      variant="outlined"
                      sx={{ mr: 1, mb: 0.5 }}
                    />
                    <Chip 
                      label={address.village}
                      size="small"
                      color="secondary"
                      variant="outlined"
                      sx={{ mr: 1, mb: 0.5 }}
                    />
                    <Chip 
                      label={`${address.neighborhood}鄰`}
                      size="small"
                      variant="outlined"
                      sx={{ mb: 0.5 }}
                    />
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" component="div">
                    {buildFullAddress(address)}
                  </Typography>
                  {address.full_address && address.full_address !== buildFullAddress(address) && (
                    <Typography variant="caption" color="text.secondary">
                      {address.full_address}
                    </Typography>
                  )}
                </TableCell>
                <TableCell>
                  {address.x_coord && address.y_coord ? (
                    <Box>
                      <Typography variant="caption" component="div">
                        經度: {address.x_coord.toFixed(6)}
                      </Typography>
                      <Typography variant="caption" component="div">
                        緯度: {address.y_coord.toFixed(6)}
                      </Typography>
                    </Box>
                  ) : (
                    <Typography variant="caption" color="text.secondary">
                      無座標資料
                    </Typography>
                  )}
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="查看詳細資訊">
                    <IconButton
                      size="small"
                      onClick={() => handleAddressClick(address)}
                      color="primary"
                    >
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  {address.x_coord && address.y_coord && (
                    <Tooltip title="在地圖上顯示">
                      <IconButton
                        size="small"
                        onClick={() => handleAddressClick(address)}
                        color="secondary"
                      >
                        <LocationIcon />
                      </IconButton>
                    </Tooltip>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 分頁 */}
      {showPagination && (
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50, 100]}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPageState}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="每頁顯示:"
          labelDisplayedRows={({ from, to, count }) => 
            `${from}-${to} 共 ${count !== -1 ? count : `超過 ${to}`} 筆`
          }
        />
      )}
    </Box>
  );
};
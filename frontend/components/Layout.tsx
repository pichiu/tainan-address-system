/**
 * 應用程式主要版面配置元件
 */
import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Paper,
  Link,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  GitHub as GitHubIcon,
  Info as InfoIcon,
  Map as MapIcon
} from '@mui/icons-material';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* 頂部導航列 */}
      <AppBar position="static" color="primary">
        <Toolbar>
          <MapIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            臺南市門牌坐標查詢系統
          </Typography>
          
          <Chip 
            label="v1.0.0"
            size="small"
            variant="outlined"
            sx={{ 
              color: 'white', 
              borderColor: 'white',
              mr: 2
            }}
          />
          
          <Tooltip title="關於系統">
            <IconButton color="inherit" size="small">
              <InfoIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="GitHub Repository">
            <IconButton 
              color="inherit" 
              size="small"
              component="a"
              href="https://github.com/pichiu/tainan-address-system"
              target="_blank"
              rel="noopener noreferrer"
            >
              <GitHubIcon />
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* 主要內容區域 */}
      <Box component="main" sx={{ flexGrow: 1, py: 3, bgcolor: 'grey.50' }}>
        <Container maxWidth="xl">
          {children}
        </Container>
      </Box>

      {/* 頁腳 */}
      <Paper 
        component="footer" 
        sx={{ 
          mt: 'auto',
          py: 3,
          px: 2,
          bgcolor: 'grey.100'
        }}
      >
        <Container maxWidth="xl">
          <Box sx={{ 
            display: 'flex', 
            flexDirection: { xs: 'column', md: 'row' },
            justifyContent: 'space-between',
            alignItems: { xs: 'center', md: 'flex-start' },
            gap: 2
          }}>
            {/* 系統資訊 */}
            <Box sx={{ textAlign: { xs: 'center', md: 'left' } }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                臺南市門牌坐標查詢系統
              </Typography>
              <Typography variant="caption" color="text.secondary">
                基於政府開放資料，提供便民的地址查詢服務
              </Typography>
            </Box>

            {/* 資料來源資訊 */}
            <Box sx={{ textAlign: { xs: 'center', md: 'right' } }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                資料來源
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                <Typography variant="caption" color="text.secondary">
                  臺南市政府 113年 臺南市門牌坐標資料
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, justifyContent: { xs: 'center', md: 'flex-end' } }}>
                  <Link 
                    href="https://data.gov.tw/license" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    variant="caption"
                    underline="hover"
                  >
                    政府資料開放授權條款
                  </Link>
                  <span>•</span>
                  <Link 
                    href="https://github.com/pichiu/tainan-address-system" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    variant="caption"
                    underline="hover"
                  >
                    開源專案
                  </Link>
                </Box>
              </Box>
            </Box>
          </Box>

          {/* 版權聲明 */}
          <Box sx={{ 
            mt: 2, 
            pt: 2, 
            borderTop: 1, 
            borderColor: 'grey.300',
            textAlign: 'center'
          }}>
            <Typography variant="caption" color="text.secondary">
              © 2024 臺南市門牌坐標查詢系統. 本專案採用 MIT License 開源授權.
            </Typography>
          </Box>
        </Container>
      </Paper>
    </Box>
  );
};
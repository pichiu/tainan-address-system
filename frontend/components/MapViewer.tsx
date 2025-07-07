/**
 * 地圖顯示元件
 */
import React, { useEffect, useRef, useState } from 'react';
import { Box, Alert, CircularProgress, Typography, IconButton, Tooltip } from '@mui/material';
import { MyLocation, ZoomIn, ZoomOut, Layers } from '@mui/icons-material';
import dynamic from 'next/dynamic';
import type { MapViewerProps, Address } from '../services/types';

// 動態載入 Leaflet 相關元件（避免 SSR 問題）
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });
const useMap = dynamic(() => import('react-leaflet').then(mod => mod.useMap), { ssr: false });

// 預設設定
const DEFAULT_CENTER: [number, number] = [23.0, 120.2]; // 臺南市中心
const DEFAULT_ZOOM = 12;
const TAIWAN_BOUNDS: [[number, number], [number, number]] = [
  [21.8, 119.3], // 西南角
  [25.3, 122.0]  // 東北角
];

// 地圖控制元件
const MapController: React.FC<{
  addresses: Address[];
  onAddressClick?: (address: Address) => void;
}> = ({ addresses, onAddressClick }) => {
  const map = useMap();

  useEffect(() => {
    if (addresses.length > 0) {
      // 計算所有地址的邊界
      const validAddresses = addresses.filter(addr => 
        addr.x_coord && addr.y_coord && 
        addr.y_coord >= 21.8 && addr.y_coord <= 25.3 &&
        addr.x_coord >= 119.3 && addr.x_coord <= 122.0
      );

      if (validAddresses.length > 0) {
        if (validAddresses.length === 1) {
          // 單一地址，直接定位
          const addr = validAddresses[0];
          map.setView([addr.y_coord!, addr.x_coord!], 16);
        } else {
          // 多個地址，調整視野以包含所有地址
          const bounds = validAddresses.map(addr => [addr.y_coord!, addr.x_coord!] as [number, number]);
          map.fitBounds(bounds, { padding: [20, 20] });
        }
      }
    }
  }, [addresses, map]);

  return null;
};

// 地址標記元件
const AddressMarkers: React.FC<{
  addresses: Address[];
  onAddressClick?: (address: Address) => void;
}> = ({ addresses, onAddressClick }) => {
  // 自訂圖標（使用 Leaflet 預設圖標）
  const [L, setL] = useState<any>(null);

  useEffect(() => {
    // 動態載入 Leaflet
    import('leaflet').then((leaflet) => {
      setL(leaflet);
      
      // 修復 Leaflet 圖標路徑問題
      delete (leaflet.Icon.Default.prototype as any)._getIconUrl;
      leaflet.Icon.Default.mergeOptions({
        iconRetinaUrl: '/images/marker-icon-2x.png',
        iconUrl: '/images/marker-icon.png',
        shadowUrl: '/images/marker-shadow.png',
      });
    });
  }, []);

  if (!L) return null;

  const validAddresses = addresses.filter(addr => 
    addr.x_coord && addr.y_coord && 
    addr.y_coord >= 21.8 && addr.y_coord <= 25.3 &&
    addr.x_coord >= 119.3 && addr.x_coord <= 122.0
  );

  return (
    <>
      {validAddresses.map((address, index) => (
        <Marker
          key={`${address.id}-${index}`}
          position={[address.y_coord!, address.x_coord!]}
          eventHandlers={{
            click: () => onAddressClick?.(address)
          }}
        >
          <Popup>
            <Box sx={{ minWidth: 200 }}>
              <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                {address.district}{address.village}{address.neighborhood}鄰
              </Typography>
              <Typography variant="body2" gutterBottom>
                {address.full_address}
              </Typography>
              {address.distance && (
                <Typography variant="caption" color="text.secondary">
                  距離: {address.distance.toFixed(0)} 公尺
                </Typography>
              )}
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  座標: {address.y_coord?.toFixed(6)}, {address.x_coord?.toFixed(6)}
                </Typography>
              </Box>
            </Box>
          </Popup>
        </Marker>
      ))}
    </>
  );
};

// 主要地圖元件
export const MapViewer: React.FC<MapViewerProps> = ({
  addresses,
  center = DEFAULT_CENTER,
  zoom = DEFAULT_ZOOM,
  onAddressClick,
  height = 400
}) => {
  const [isClient, setIsClient] = useState(false);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [mapError, setMapError] = useState<string | null>(null);
  const mapRef = useRef<any>(null);

  // 確保在客戶端渲染
  useEffect(() => {
    setIsClient(true);
  }, []);

  // 處理地圖載入
  const handleMapLoad = () => {
    setMapLoaded(true);
    setMapError(null);
  };

  // 處理地圖錯誤
  const handleMapError = (error: any) => {
    console.error('Map error:', error);
    setMapError('地圖載入失敗');
  };

  // 地圖控制函數
  const handleZoomIn = () => {
    if (mapRef.current) {
      mapRef.current.zoomIn();
    }
  };

  const handleZoomOut = () => {
    if (mapRef.current) {
      mapRef.current.zoomOut();
    }
  };

  const handleMyLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          if (mapRef.current) {
            mapRef.current.setView([latitude, longitude], 16);
          }
        },
        (error) => {
          console.error('Geolocation error:', error);
        }
      );
    }
  };

  // 如果不是客戶端，顯示載入中
  if (!isClient) {
    return (
      <Box 
        sx={{ 
          height, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          border: '1px solid #ddd',
          borderRadius: 1
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // 如果發生錯誤，顯示錯誤訊息
  if (mapError) {
    return (
      <Alert severity="error" sx={{ height }}>
        {mapError}
      </Alert>
    );
  }

  const validAddressCount = addresses.filter(addr => 
    addr.x_coord && addr.y_coord
  ).length;

  return (
    <Box sx={{ position: 'relative', height, border: '1px solid #ddd', borderRadius: 1 }}>
      {/* 地圖載入提示 */}
      {!mapLoaded && (
        <Box 
          sx={{ 
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(255, 255, 255, 0.8)',
            zIndex: 1000
          }}
        >
          <CircularProgress />
        </Box>
      )}

      {/* 地圖控制按鈕 */}
      <Box sx={{ 
        position: 'absolute', 
        top: 10, 
        right: 10, 
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: 1
      }}>
        <Tooltip title="放大">
          <IconButton size="small" sx={{ backgroundColor: 'white' }} onClick={handleZoomIn}>
            <ZoomIn />
          </IconButton>
        </Tooltip>
        <Tooltip title="縮小">
          <IconButton size="small" sx={{ backgroundColor: 'white' }} onClick={handleZoomOut}>
            <ZoomOut />
          </IconButton>
        </Tooltip>
        <Tooltip title="我的位置">
          <IconButton size="small" sx={{ backgroundColor: 'white' }} onClick={handleMyLocation}>
            <MyLocation />
          </IconButton>
        </Tooltip>
      </Box>

      {/* 地址統計資訊 */}
      <Box sx={{ 
        position: 'absolute', 
        bottom: 10, 
        left: 10, 
        zIndex: 1000,
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
        padding: 1,
        borderRadius: 1,
        fontSize: '0.75rem'
      }}>
        <Typography variant="caption">
          顯示 {validAddressCount} / {addresses.length} 筆地址
        </Typography>
      </Box>

      {/* Leaflet 地圖 */}
      <MapContainer
        ref={mapRef}
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        maxBounds={TAIWAN_BOUNDS}
        maxBoundsViscosity={1.0}
        whenCreated={handleMapLoad}
        onError={handleMapError}
      >
        {/* 底圖圖層 */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
        />
        
        {/* 地址標記 */}
        <AddressMarkers 
          addresses={addresses} 
          onAddressClick={onAddressClick}
        />
        
        {/* 地圖控制器 */}
        <MapController 
          addresses={addresses}
          onAddressClick={onAddressClick}
        />
      </MapContainer>
    </Box>
  );
};


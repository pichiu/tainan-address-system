# 臺南市門牌坐標查詢系統

## 專案簡介

這是一個基於政府開放資料的臺南市門牌坐標查詢系統，提供便民的地址查詢和地理位置服務。系統採用現代化的全棧架構，支援階層式地址查詢（區→村里→鄰）、關鍵字搜尋、地圖顯示等功能。

### 主要功能

- 📍 **階層式查詢**：區 → 村里 → 鄰的層級查詢
- 📊 **統計摘要**：各層級的地址統計資訊
- 🔍 **關鍵字搜尋**：支援地址關鍵字搜尋
- 🗺️ **地圖顯示**：整合 OpenStreetMap 顯示地址位置
- 📱 **響應式設計**：支援桌面和行動裝置
- 📋 **資料匯出**：支援 CSV 格式資料匯出
- ⚡ **高效能**：PostgreSQL + PostGIS 空間資料庫

### 資料來源

- **資料提供**：臺南市政府
- **資料年份**：113年
- **資料集**：臺南市門牌坐標資料
- **授權條款**：政府資料開放授權條款－第1版
- **授權網址**：https://data.gov.tw/license

## 技術架構

### 後端技術
- **Framework**：FastAPI 0.104+
- **包管理**：UV (現代 Python 包管理器)
- **資料庫**：PostgreSQL 15+ with PostGIS
- **ORM**：SQLAlchemy 2.0+
- **驗證**：Pydantic 2.0+
- **API 文檔**：自動生成 OpenAPI/Swagger

### 前端技術
- **Framework**：Next.js 14+ (App Router)
- **UI Library**：Material-UI (MUI) 5+
- **地圖**：Leaflet.js + React-Leaflet
- **狀態管理**：React Query + Zustand
- **開發語言**：TypeScript

### 部署架構
- **前端部署**：Vercel (免費)
- **後端部署**：Supabase Functions 或 Railway
- **資料庫**：Supabase PostgreSQL (免費 500MB)
- **CDN**：Vercel Edge Network

## 快速開始

### 先決條件

- Node.js 18+
- Python 3.11+
- [UV](https://github.com/astral-sh/uv) (現代 Python 包管理器) 或 pip
- PostgreSQL 15+ (帶 PostGIS 擴展)
- Git

### 1. 克隆專案

```bash
git clone https://github.com/pichiu/tainan-address-system.git
cd tainan-address-system
```

### 2. 設定環境變數

建立 `.env` 檔案：

```bash
# 後端環境變數
DATABASE_URL=postgresql://postgres:password@localhost:5432/tainan_addresses
PROJECT_NAME=臺南市門牌坐標查詢系統
VERSION=1.0.0
DEBUG=true

# 前端環境變數
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_MAP_DEFAULT_CENTER=23.0,120.2
NEXT_PUBLIC_MAP_DEFAULT_ZOOM=12
```

### 3. 使用 Docker Compose (推薦)

```bash
# 啟動所有服務
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

服務將在以下埠號啟動：
- 前端：http://localhost:3000
- 後端 API：http://localhost:8000
- API 文檔：http://localhost:8000/api/v1/docs
- pgAdmin：http://localhost:8080

### 4. 手動安裝 (開發模式)

#### 後端設定

**使用 UV (推薦)**
```bash
cd backend

# 安裝 UV (如果尚未安裝)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安裝依賴
uv sync

# 建立資料庫
createdb tainan_addresses

# 啟動服務
make run
# 或手動執行: uv run uvicorn app.main:app --reload
```

**使用傳統方式**
```bash
cd backend

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 建立資料庫
createdb tainan_addresses

# 啟動服務
uvicorn app.main:app --reload
```

#### 前端設定

```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發服務
npm run dev
```

## 資料匯入

### 1. 準備 CSV 檔案

確保您的 CSV 檔案包含以下欄位：
```
區,村里,鄰,街、路段,地區,巷,弄,號,橫座標,縱座標
```

### 2. 執行匯入

**使用 UV**
```bash
cd backend

# 匯入資料（會清空現有資料）
make import-data file=/path/to/your/data.csv args="--clear"

# 分批匯入（不清空現有資料）
make import-data file=/path/to/your/data.csv args="--chunk-size 5000"

# 或手動執行
uv run python -m app.utils.data_import /path/to/your/data.csv --clear
```

**使用傳統方式**
```bash
cd backend

# 匯入資料（會清空現有資料）
python -m app.utils.data_import /path/to/your/data.csv --clear

# 分批匯入（不清空現有資料）
python -m app.utils.data_import /path/to/your/data.csv --chunk-size 5000
```

### 3. 驗證匯入結果

```bash
# 檢查資料統計
curl http://localhost:8000/api/v1/stats/overview
```

## API 文檔

完整的 API 文檔在系統啟動後可以通過以下網址查看：

- **Swagger UI**：http://localhost:8000/api/v1/docs
- **ReDoc**：http://localhost:8000/api/v1/redoc

### 主要 API 端點

```
GET  /api/v1/districts                     # 取得所有區
GET  /api/v1/villages?district={district}  # 取得指定區的村里
GET  /api/v1/neighborhoods?district={}&village={}  # 取得鄰

GET  /api/v1/summary/district/{district}   # 區統計摘要
GET  /api/v1/summary/village/{district}/{village}  # 村里統計摘要
GET  /api/v1/details/neighborhood/{district}/{village}/{neighborhood}  # 鄰詳細資料

GET  /api/v1/search?q={}&district={}&village={}  # 地址搜尋
GET  /api/v1/geo/nearby?lat={}&lng={}&radius={}  # 地理位置查詢

GET  /api/v1/license                       # 資料授權資訊
GET  /api/v1/health                        # 健康檢查
```

## 部署指南

詳細的生產環境部署指南請參考：[部署指南](docs/DEPLOYMENT.md)

### 快速部署到 Vercel + Supabase

1. **Fork 此專案**到您的 GitHub

2. **建立 Supabase 專案**
   - 前往 [Supabase](https://supabase.com) 建立專案
   - 啟用 PostGIS 擴展
   - 執行 SQL 建立資料表結構

3. **部署到 Vercel**
   - 連結 GitHub repository
   - 設定環境變數
   - 自動部署

4. **匯入資料**
   - 使用本地匯入腳本將資料匯入 Supabase

## 專案結構

```
tainan-address-system/
├── backend/                     # FastAPI 後端
│   ├── app/
│   │   ├── api/                # API 路由
│   │   ├── core/               # 核心設定
│   │   ├── models/             # 資料模型
│   │   ├── schemas/            # API 模型
│   │   ├── services/           # 業務邏輯
│   │   └── utils/              # 工具函數
│   ├── alembic/                # 資料庫遷移
│   ├── pyproject.toml          # Python 專案配置 (UV)
│   ├── uv.lock                 # 依賴鎖定檔案
│   ├── requirements.txt        # 傳統依賴檔案 (向後相容)
│   ├── Makefile                # 開發指令
│   └── Dockerfile              # 容器配置
├── frontend/                   # Next.js 前端
│   ├── components/             # React 元件
│   ├── hooks/                  # 自訂 Hooks
│   ├── pages/                  # 頁面路由
│   ├── services/               # API 服務
│   ├── package.json
│   └── Dockerfile
├── docs/                       # 文檔
├── data/                       # 資料檔案
├── docker-compose.yml          # 開發環境
├── .env.example                # 環境變數範例
└── README.md
```

## 功能截圖

### 主搜尋介面
![主搜尋介面](docs/images/main-search.png)

### 統計摘要
![統計摘要](docs/images/summary-stats.png)

### 地圖顯示
![地圖顯示](docs/images/map-view.png)

### 詳細資料表格
![詳細資料表格](docs/images/data-table.png)

## 開發指南

### 現代化開發工具

本專案使用 **UV** 作為 Python 包管理器，帶來以下優勢：
- **⚡ 極速安裝**：比 pip 快 10-100 倍
- **🔒 確定性建置**：uv.lock 確保一致的依賴版本
- **📦 現代配置**：pyproject.toml 取代 requirements.txt
- **🛠️ 統一工具鏈**：安裝、解析、虛擬環境一體化

### 程式碼規範

- **Python**：遵循 PEP 8，使用 Black 格式化
- **TypeScript**：遵循 ESLint 規則
- **Git**：使用 Conventional Commits

### 測試

**後端測試**
```bash
cd backend

# 使用 UV
make test
# 或: uv run pytest

# 使用傳統方式
pytest
```

**前端測試**
```bash
cd frontend
npm test
```

### 程式碼格式化

**Python (使用 UV)**
```bash
cd backend
make format  # 執行 black 和 isort
make lint    # 執行 flake8 和 mypy
make check   # 執行所有檢查
```

**Python (傳統方式)**
```bash
cd backend
black app/
isort app/
flake8 app/
mypy app/
```

**TypeScript**
```bash
cd frontend
npm run lint:fix
```

## 貢獻指南

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 授權條款

### 程式碼授權
本專案程式碼採用 MIT License。詳見 [LICENSE](LICENSE) 檔案。

### 資料授權
資料來源：臺南市政府 113年 臺南市門牌坐標資料

此開放資料依政府資料開放授權條款 (Open Government Data License) 進行公眾釋出，使用者於遵守本條款各項規定之前提下，得利用之。

授權條款：https://data.gov.tw/license

## 常見問題

### Q: 如何更新資料？
A: 重新執行資料匯入腳本，使用 `--clear` 參數清空舊資料。

### Q: 支援其他縣市的資料嗎？
A: 目前專門針對臺南市設計，但架構可以擴展支援其他縣市。

### Q: 地圖不顯示怎麼辦？
A: 檢查瀏覽器控制台錯誤，確認 Leaflet 資源載入正常。

### Q: API 回應很慢怎麼辦？
A: 檢查資料庫索引是否建立完成，考慮增加快取機制。

## 聯絡資訊

- **專案維護者**：[Pi](mailto:rtchiou@gmail.com)
- **問題回報**：[GitHub Issues](https://github.com/pichiu/tainan-address-system/issues)
- **功能建議**：[GitHub Discussions](https://github.com/pichiu/tainan-address-system/discussions)

## 更新日誌

### v1.0.0 (2024-01-XX)
- 🎉 初始版本發布
- ✨ 完整的地址查詢功能
- 🗺️ 地圖整合顯示
- 📱 響應式設計
- 🚀 生產環境部署支援

---

**感謝使用臺南市門牌坐標查詢系統！** 如果您覺得這個專案有用，請給我們一個 ⭐ Star！


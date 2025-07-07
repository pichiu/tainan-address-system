# 臺南市門牌坐標查詢系統 - 後端

基於 FastAPI 的地址查詢 API 系統，支援階層式地址查詢、地理空間搜尋和統計分析。

## 技術棧

- **框架**: FastAPI 0.104+
- **資料庫**: PostgreSQL 15+ with PostGIS
- **ORM**: SQLAlchemy 2.0+
- **包管理**: UV (現代 Python 包管理器)
- **遷移**: Alembic
- **驗證**: Pydantic 2.0+
- **容器化**: Docker

## 快速開始

### 先決條件

- Python 3.11+
- [UV](https://github.com/astral-sh/uv) (推薦) 或 pip
- PostgreSQL 15+ (帶 PostGIS 擴展)

### 安裝 UV

```bash
# macOS 和 Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 專案設置

```bash
# 克隆專案
git clone https://github.com/pichiu/tainan-address-system.git
cd tainan-address-system/backend

# 安裝依賴
make install-dev
# 或手動執行
uv sync

# 設置環境變數
cp .env.example .env
# 編輯 .env 檔案配置資料庫等設定

# 初始化資料庫
make upgrade
# 或手動執行
uv run alembic upgrade head

# 啟動開發服務器
make run
# 或手動執行
uv run uvicorn app.main:app --reload
```

### 使用 Docker (推薦)

```bash
# 從專案根目錄啟動完整服務
docker-compose up -d

# 僅啟動後端和資料庫
docker-compose up -d postgres backend
```

## 開發指令

所有常用指令都已整理在 Makefile 中：

```bash
# 查看所有可用指令
make help

# 安裝依賴
make install          # 僅生產依賴
make install-dev      # 包含開發依賴

# 執行服務
make run              # 開發服務器

# 測試
make test             # 執行測試
make test-cov         # 執行測試並生成覆蓋率報告

# 程式碼品質
make format           # 格式化程式碼 (black, isort)
make lint             # 執行 linting (flake8, mypy)
make check            # 執行所有檢查

# 資料庫管理
make migration message="描述"  # 建立新遷移
make upgrade          # 應用遷移
make downgrade        # 回滾遷移

# 清理
make clean            # 清理快取和臨時檔案
```

### 手動指令 (不使用 Makefile)

```bash
# 安裝和管理依賴
uv add package_name           # 新增包
uv add --dev package_name     # 新增開發依賴
uv remove package_name        # 移除包
uv sync                       # 同步依賴
uv lock                       # 更新 lock 檔案

# 執行指令
uv run python script.py       # 執行 Python 腳本
uv run pytest               # 執行測試
uv run uvicorn app.main:app --reload  # 啟動服務器

# 程式碼品質
uv run black .               # 格式化
uv run isort .               # 排序 imports
uv run flake8 .              # Linting
uv run mypy .                # 類型檢查
```

## 資料匯入

```bash
# 使用 Makefile
make import-data file=data.csv args="--clear"

# 手動執行
uv run python -m app.utils.data_import data.csv --clear --chunk-size 5000
```

## API 文檔

啟動服務後可以通過以下網址查看 API 文檔：

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 專案結構

```
backend/
├── app/                          # 主要應用程式
│   ├── api/                     # API 路由
│   │   ├── deps.py             # 依賴注入
│   │   └── endpoints/          # API 端點
│   ├── core/                   # 核心配置
│   │   ├── config.py          # 應用設定
│   │   └── database.py        # 資料庫連線
│   ├── models/                 # SQLAlchemy 模型
│   ├── schemas/                # Pydantic 模型
│   ├── services/               # 業務邏輯層
│   └── utils/                  # 工具函數
├── alembic/                    # 資料庫遷移
├── tests/                      # 測試檔案
├── pyproject.toml              # 專案配置和依賴
├── uv.lock                     # 依賴鎖定檔案
├── Makefile                    # 常用指令
├── Dockerfile                  # Docker 配置
└── .pre-commit-config.yaml     # Git hooks
```

## 環境變數

詳見 `.env.example` 檔案中的完整配置說明。

主要環境變數：

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/tainan_addresses
PROJECT_NAME=臺南市門牌坐標查詢系統
DEBUG=false
API_V1_STR=/api/v1
```

## 部署

### 使用 Docker

```bash
# 構建生產映像
docker build -t tainan-address-backend .

# 執行容器
docker run -p 8000:8000 -e DATABASE_URL=your_db_url tainan-address-backend
```

### 使用 UV

```bash
# 安裝生產依賴
uv sync --no-dev

# 使用 Gunicorn 執行 (生產環境)
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 開發工具

- **程式碼格式化**: Black, isort
- **Linting**: Flake8, MyPy
- **測試**: pytest
- **Pre-commit hooks**: 自動程式碼檢查
- **依賴管理**: UV (比 pip 快 10-100 倍)

## 效能

- **UV 包管理**: 顯著提升依賴安裝和解析速度
- **資料庫索引**: 針對常用查詢優化
- **非同步處理**: FastAPI 的原生非同步支援
- **連線池**: SQLAlchemy 連線池管理

## 貢獻

1. Fork 專案
2. 建立功能分支: `git checkout -b feature/amazing-feature`
3. 安裝 pre-commit hooks: `make dev-setup`
4. 進行更改並確保測試通過: `make check`
5. 提交更改: `git commit -m 'Add amazing feature'`
6. 推送分支: `git push origin feature/amazing-feature`
7. 開啟 Pull Request

## 授權

MIT License - 詳見 [LICENSE](../LICENSE) 檔案。
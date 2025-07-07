# 使用官方 Python 3.11 slim 映像
FROM python:3.11-slim as base

# 設置環境變數
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安裝 UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 建立工作目錄
WORKDIR /app

# 複製專案配置檔案
COPY pyproject.toml uv.lock ./

# 安裝 Python 依賴
RUN uv sync --frozen --no-dev

# 複製應用程式碼
COPY . .

# 建立非 root 用戶
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# 暴露連接埠
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# 啟動命令
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# 開發階段 (多階段構建)
FROM base as development

# 安裝開發依賴
RUN uv sync --frozen

# 使用開發模式啟動
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
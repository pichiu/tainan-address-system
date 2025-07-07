# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack Tainan City address coordinate query system built with FastAPI backend and Next.js frontend. The system provides hierarchical address lookup (district → village → neighborhood), keyword search, map visualization, and data export functionality using government open data.

## Development Commands

### Backend (FastAPI)
```bash
# Setup virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Data import
python -m app.utils.data_import /path/to/data.csv --clear
python -m app.utils.data_import /path/to/data.csv --chunk-size 5000

# Run tests
pytest
```

### Frontend (Next.js)
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Lint code
npm run lint
```

### Docker Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Architecture

### Backend Structure
- **FastAPI Application**: Located in `backend/app/`
- **Core Configuration**: `app/core/config.py` - centralized settings with Pydantic
- **Database Models**: `app/models/address.py` - SQLAlchemy models with PostGIS geometry support
- **API Endpoints**: `app/api/endpoints/` - hierarchical address queries, search, geo-spatial queries
- **Data Import**: `app/utils/data_import.py` - CSV import with coordinate transformation (TWD97 to WGS84)
- **Database**: PostgreSQL with PostGIS extension for spatial queries

### Frontend Structure
- **Next.js 14 App Router**: React application with TypeScript
- **UI Components**: Material-UI (MUI) components in `components/`
- **State Management**: React Query + Zustand for API state and local state
- **Map Integration**: Leaflet.js with React-Leaflet for map visualization
- **Custom Hooks**: `hooks/useAddressSearch.ts` for address search logic

### Key Data Models
- **Address Model**: Contains district, village, neighborhood, street details, coordinates, and PostGIS geometry
- **AddressStats Model**: Cached statistics for performance optimization
- **Coordinate System**: TWD97 (EPSG:3826) transformed to WGS84 (EPSG:4326)

### API Endpoints Structure
- `/api/v1/districts` - Get all districts
- `/api/v1/villages?district=` - Get villages by district
- `/api/v1/neighborhoods?district=&village=` - Get neighborhoods
- `/api/v1/summary/district/{district}` - District statistics
- `/api/v1/summary/village/{district}/{village}` - Village statistics
- `/api/v1/details/neighborhood/{district}/{village}/{neighborhood}` - Full neighborhood data
- `/api/v1/search` - Flexible address search with pagination
- `/api/v1/geo/nearby` - Geospatial proximity search
- `/api/v1/export/csv` - CSV data export

## Database Schema

### Core Tables
- **addresses**: Main address table with geometry column, indexed by district/village/neighborhood
- **address_stats**: Cached statistics table for performance, updated during data import

### Important Indexes
- `idx_district_village` - Composite index for hierarchical queries
- `idx_coordinates` - Spatial index for coordinate-based queries
- PostGIS spatial indexes on geometry column

## Data Import Process

1. **CSV Validation**: Validates required columns (區, 村里, 鄰, 橫座標, 縱座標)
2. **Coordinate Transformation**: Converts TWD97 to WGS84 using pyproj
3. **Data Cleaning**: Normalizes text, handles duplicates, validates coordinate bounds
4. **Batch Processing**: Processes data in configurable chunks (default 5000)
5. **Geometry Creation**: Creates PostGIS geometry from coordinates
6. **Statistics Update**: Updates cached statistics for performance

## Environment Configuration

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `NEXT_PUBLIC_API_URL`: Frontend API base URL
- `NEXT_PUBLIC_MAP_DEFAULT_CENTER`: Default map center coordinates
- `NEXT_PUBLIC_MAP_DEFAULT_ZOOM`: Default map zoom level

## Testing and Code Quality

### Backend
- Use `pytest` for Python testing
- Code formatting with `black` and `isort`
- Type checking with Pydantic models

### Frontend
- Use `npm test` for React testing
- ESLint configuration for code quality
- TypeScript for type safety

## Performance Considerations

- **Database Indexing**: Composite indexes on frequently queried columns
- **Statistics Caching**: Pre-computed statistics in separate table
- **Batch Processing**: Configurable chunk sizes for large dataset imports
- **Spatial Queries**: PostGIS for efficient geographic queries with fallback to Haversine formula
- **Pagination**: All search endpoints support pagination

## Common Development Patterns

- **Error Handling**: Consistent APIResponse format with success/error states
- **Validation**: Pydantic schemas for request/response validation
- **Logging**: Structured logging throughout the application
- **CORS**: Configured for local development and production environments
- **Database Transactions**: Proper transaction handling in data import
# System Architecture & Technical Design

## Overview
**Tamil Nadu Farmer Rain Alert & Marketplace** is built as a resilient, accessible, low-bandwidth web service providing timely rain alerts to Tamil Nadu farmers, followed by an agricultural marketplace.

```mermaid
flowchart TD
    subgraph Frontend ["Frontend (Lightweight Vanilla JS + Jinja2)"]
        UI_LANG[Language Selection ta / en]
        UI_THEME[Monochrome Theme Light/Dark]
        UI_DASH[Farmer Dashboard & Alerts]
        UI_MAP[Leaflet Rain Map]
    end

    subgraph Backend ["FastAPI Application (Python 3.12+)"]
        API[REST API /api/v1]
        I18N[i18n Service ta.json / en.json]
        AUTH[OTP Auth & Session]
        RAIN[Rain Analysis Engine]
        ALERT[Alert & Dedup Service]
    end

    subgraph Storage ["PostgreSQL 16 + PostGIS"]
        DB[(PostGIS Spatial DB)]
        LOC[Locations Hierarchy]
        FARMERS[Farmers & Preferences]
        WEATHER[Weather & Forecast Cache]
    end

    subgraph External ["External Integrations"]
        IMD[IMD Observations & Warnings]
        FORECAST[Point Forecast API]
        SMS[SMS Gateway / TRAI DLT]
        WA[WhatsApp Cloud API]
    end

    UI_LANG --> I18N
    UI_DASH --> API
    API --> AUTH
    API --> DB
    RAIN --> ALERT
    ALERT --> SMS
    ALERT --> WA
    FORECAST --> RAIN
    IMD --> RAIN
```

## Phase 1 Implementation Scope
- FastAPI application core and `/health`, `/ready` endpoints.
- PostgreSQL + PostGIS schema initialization with Alembic.
- Core models: `Farmer` (with language & theme preferences) and `Location` (with PostGIS spatial centroid).
- Internationalization module (`i18n.py`) supporting Tamil (`ta`) and English (`en`) with fallback and key-parity testing.
- First-screen language selection flow and monochrome design system (WCAG 2.1 AA, `>=44px` tap targets, CSS custom properties).

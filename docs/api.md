# API Specification

## Conventions
- **Base URI**: `/api/v1`
- **Format**: JSON (`Content-Type: application/json; charset=utf-8`)
- **Localization**: Controlled via query param `?lang=ta`, cookie `tn_farmer_lang`, or header `Accept-Language: ta|en`.

## Phase 1 Endpoints

### Health & Readiness
- `GET /health`: Liveness probe returning status, app name, and environment.
- `GET /ready`: Readiness probe verifying database connectivity.

### Preferences
- `GET /api/v1/preferences`: Returns current language and visual theme.
- `POST /api/v1/preferences/language`: Body `{"language": "ta"|"en"}`. Sets 1-year persistent cookie.
- `POST /api/v1/preferences/theme`: Body `{"theme": "light"|"dark"|"system"}`. Sets 1-year persistent cookie.

## Phase 2+ Endpoints (Upcoming)
- `POST /api/v1/auth/send-otp`
- `POST /api/v1/auth/verify-otp`
- `GET /api/v1/farmers/me`
- `GET /api/v1/weather`
- `GET /api/v1/rain-alerts`
- `GET /api/v1/products`

# Database Architecture & Retention Policy

## Technology
- **Engine**: PostgreSQL 16
- **Spatial Extension**: PostGIS 3.4
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic

## Core Models (Phase 1)

### `locations`
| Column | Type | Nullable | Notes |
| :--- | :--- | :--- | :--- |
| `id` | UUID | No | Primary Key |
| `name_en` | VARCHAR(120) | No | English Name |
| `name_ta` | VARCHAR(120) | No | Tamil Name |
| `level` | VARCHAR(20) | No | 'district', 'taluk', 'village' |
| `parent_id` | UUID | Yes | Self-referencing FK |
| `lgd_code` | VARCHAR(30) | Yes | Local Government Directory Code |
| `centroid` | GEOMETRY(POINT, 4326) | Yes | PostGIS Centroid with GiST Index |
| `latitude` | FLOAT | Yes | Cached WGS84 latitude |
| `longitude`| FLOAT | Yes | Cached WGS84 longitude |

### `farmers`
| Column | Type | Nullable | Notes |
| :--- | :--- | :--- | :--- |
| `id` | UUID | No | Primary Key |
| `name` | VARCHAR(150) | Yes | Farmer name |
| `phone_hash` | VARCHAR(64) | Yes | SHA-256 hash for secure lookup |
| `phone_encrypted` | VARCHAR(255) | Yes | Encrypted mobile for delivery |
| `language` | VARCHAR(5) | No | Default: 'ta' ('ta' or 'en') |
| `theme_preference`| VARCHAR(10) | No | Default: 'system' ('light', 'dark', 'system') |
| `district` | VARCHAR(100) | Yes | District name |
| `taluk` | VARCHAR(100) | Yes | Taluk name |
| `village` | VARCHAR(100) | Yes | Village name |
| `location_id` | UUID | Yes | FK to `locations.id` |
| `is_consent_given`| BOOLEAN | No | India DPDP Act explicit consent |
| `is_active` | BOOLEAN | No | Active status |
| `is_deleted` | BOOLEAN | No | Soft-delete flag |

## Retention Policy
- Forecast data: Partitioned monthly, pruned after 90 days.
- Observation data: Retained for 2 years for historical calibration.
- Farmer data: Retained until account deletion request (DPDP Act).

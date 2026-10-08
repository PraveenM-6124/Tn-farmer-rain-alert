# ADR-001: Architecture, Localization, and Monochrome UI Foundations

## Status
Accepted

## Context
Tamil Nadu farmers often operate in low-bandwidth rural conditions with low-cost Android phones. Heavy SPA frameworks (e.g. Next.js, React) create high latency, large bundle sizes, and battery drain. Furthermore, weather alerts must be immediately accessible in Tamil and English with high visual contrast under direct sunlight.

## Decisions
1. **Frontend**: Use server-rendered Jinja2 templates styled with vanilla CSS custom properties (tokens) and lightweight vanilla JavaScript. No heavy client-side frameworks.
2. **Visual Identity**: Strict monochrome design system (#000000 / #FFFFFF) with persistent light/dark mode and WCAG 2.1 AA compliance. Semantic color is strictly reserved for weather severity and accompanied by icons/text.
3. **First-Screen Language Gate**: Require language selection upon first visit (`ta` or `en`) prior to any dashboard display. Store in cookie and sync to DB upon login.
4. **Backend**: FastAPI with Python 3.12, PostgreSQL 16 + PostGIS for spatial queries, GeoAlchemy2, and Alembic migrations.
5. **Testing**: Strict key parity between `translations/en.json` and `translations/ta.json`, CI pipeline enforcing formatting, linting, and 80%+ test coverage.

## Consequences
- Fast initial page loads on 3G (<100KB payload).
- Maximum clarity under outdoor sunlight.
- Robust localization without hardcoded strings.

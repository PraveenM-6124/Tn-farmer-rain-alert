# Contributing to Tamil Nadu Farmer Rain Alert & Marketplace

Thank you for your interest in contributing!

## Code of Conduct
We are committed to providing a welcoming, inclusive, and professional environment for everyone.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/tn-farmer-rain-alert.git
   cd tn-farmer-rain-alert
   ```

2. **Create Python virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   pre-commit install
   ```

4. **Environment variables**:
   ```bash
   cp .env.example .env
   ```

5. **Start PostgreSQL + PostGIS (via Docker)**:
   ```bash
   docker compose up -d postgres
   ```

6. **Run tests**:
   ```bash
   pytest
   ```

## Commit Conventions
We strictly follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` A new feature
- `fix:` A bug fix
- `docs:` Documentation only changes
- `style:` Code style / formatting changes
- `refactor:` A code change that neither fixes a bug nor adds a feature
- `perf:` A code change that improves performance
- `test:` Adding missing tests or correcting existing tests
- `chore:` Changes to the build process or auxiliary tools

## Definition of Done
Every pull request must:
- Pass all unit and integration tests.
- Maintain type hints and pass `mypy`.
- Pass `ruff` linting and formatting.
- Not leak any PII or secrets.
- Maintain key parity between `translations/en.json` and `translations/ta.json`.

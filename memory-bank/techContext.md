# Tech Context: Endurain

## Technologies Used

*   **Frontend:**
    *   Framework: Vue.js (likely Vue 3 based on modern practices)
    *   UI Library: Bootstrap CSS (for styling and components)
    *   Notifications: Notivue
    *   Build Tool: Vite
    *   Package Manager: npm
    *   Testing: Vitest (implied by `vitest.config.js`)
    *   Linting/Formatting: ESLint, Prettier (implied by config files)
    *   Internationalization (i18n): Handled via JSON files in `frontend/app/src/i18n/`
*   **Backend:**
    *   Framework: Python FastAPI
    *   Language: Python (version not specified, but likely 3.7+)
    *   Database ORM: SQLAlchemy
    *   Database Migrations: Alembic
    *   Package Manager: Poetry
    *   Integrations:
        *   Strava: `stravalib`
        *   Garmin Connect: `python-garminconnect`
    *   File Parsing:
        *   GPX: `gpxpy`
        *   FIT: `fitdecode`
    *   Asynchronous Operations: FastAPI leverages `asyncio`.
*   **Database:**
    *   Options: PostgreSQL or MariaDB
*   **Observability:**
    *   Tracing: Jaeger
*   **Deployment:**
    *   Containerization: Docker, Docker Compose

## Development Setup

*   The project uses Docker Compose (`docker-compose.yml.example`) for setting up the development environment (frontend, backend, database).
*   Configuration is managed via environment variables (referenced in `backend/app/core/config.py` and `frontend/app/.env`).
*   Backend dependencies are managed by Poetry (`pyproject.toml`, `poetry.lock`).
*   Frontend dependencies are managed by npm (`package.json`, `package-lock.json`).

## Technical Constraints

*   Requires Docker for deployment/development.
*   Relies on external APIs for Strava and Garmin Connect integration, which might have rate limits or require API keys.
*   Database choice (PostgreSQL/MariaDB) might influence specific SQL syntax or features used, although SQLAlchemy aims to abstract this.

## Dependencies

*   **Backend:** See `backend/pyproject.toml` for a full list. Key dependencies include `fastapi`, `sqlalchemy`, `alembic`, `psycopg2-binary` (for Postgres) or `mysqlclient` (for MariaDB), `stravalib`, `python-garminconnect`, `gpxpy`, `fitdecode`.
*   **Frontend:** See `frontend/app/package.json` for a full list. Key dependencies include `vue`, `bootstrap`, `notivue`, `vue-router`, `pinia` (likely for state management).

# Event Planner Backend

This Flask backend includes a lightweight database setup based on Flask-SQLAlchemy to support event planning with weather awareness.

Key points:
- Default DB is SQLite (file: `event_planner.sqlite3`).
- Models: `Location`, `Event`, `WeatherSnapshot`.
- Tables auto-create on startup for development (see `app/__init__.py`). For production, migrate via Alembic/Flask-Migrate.
- On first run, a few default Locations are seeded for convenience (San Francisco, New York, London) if no locations exist.
- Configuration via environment variables (see `.env.example`).

Environment:
- Copy `.env.example` to `.env` and set:
  - OPENWEATHERMAP_API_KEY = your API key (required for live weather)
  - OPENWEATHERMAP_UNITS = metric | imperial (optional, default metric)
  - OPENWEATHERMAP_LANG = en (optional)

Run:
1. Install requirements
2. `python run.py`
3. Visit API docs at `/docs` (Swagger UI)
4. Verify Locations at `GET /api/locations/` and fetch weather at `GET /api/weather/?city=San%20Francisco&state=CA&country=US` (requires API key)

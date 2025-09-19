# Event Planner Backend

This Flask backend includes a lightweight database setup based on Flask-SQLAlchemy to support event planning with weather awareness.

Key points:
- Default DB is SQLite (file: `event_planner.sqlite3`).
- Models: `Location`, `Event`, `WeatherSnapshot`.
- Tables auto-create on startup for development (see `app/__init__.py`). For production, migrate via Alembic/Flask-Migrate.
- Configuration via environment variables (see `.env.example`).

Run:
1. Install requirements
2. `python run.py`
3. Visit API docs at `/docs` (Swagger UI)

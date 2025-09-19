from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy import select

from ..db import db
from ..models import WeatherSnapshot
from ..schemas import WeatherQuerySchema, WeatherSnapshotSchema, PaginationSchema
from ..services import (
    fetch_current_weather_by_coords,
    fetch_current_weather_by_city,
    ServiceConfigError,
    safe_now_utc,
)

blp = Blueprint(
    "Weather",
    "weather",
    url_prefix="/api/weather",
    description="Weather data from OpenWeatherMap",
)


@blp.route("/")
class WeatherQuery(MethodView):
    @blp.arguments(WeatherQuerySchema, location="query")
    @blp.response(200, WeatherSnapshotSchema)
    def get(self, args):
        """Fetch current weather by city/state/country or by lat/lon and store snapshot."""
        try:
            if args.get("lat") is not None and args.get("lon") is not None:
                payload = fetch_current_weather_by_coords(args["lat"], args["lon"])
                lat = args["lat"]
                lon = args["lon"]
                city = (payload.get("name") or None)
                state = None
                country = (payload.get("sys") or {}).get("country")
            elif args.get("city"):
                payload = fetch_current_weather_by_city(
                    args["city"], args.get("state"), args.get("country")
                )
                coord = payload.get("coord", {})
                lat = coord.get("lat")
                lon = coord.get("lon")
                city = payload.get("name")
                state = args.get("state")
                country = (payload.get("sys") or {}).get("country") or args.get("country")
            else:
                abort(400, message="Provide either lat/lon or city (with optional state/country)")
        except ServiceConfigError as sce:
            abort(503, message=str(sce))
        except Exception as exc:
            abort(502, message=f"Weather provider error: {exc}")

        snapshot = WeatherSnapshot(
            source="openweathermap",
            observed_at=safe_now_utc(),
            latitude=lat,
            longitude=lon,
            city=city,
            state=state,
            country=country,
            payload=payload,
        )
        db.session.add(snapshot)
        db.session.commit()
        return snapshot.to_dict()


@blp.route("/history")
class WeatherHistory(MethodView):
    @blp.arguments(PaginationSchema, location="query")
    @blp.response(200, WeatherSnapshotSchema(many=True))
    def get(self, args):
        """List cached weather snapshots (most recent first)."""
        page = args.get("page", 1)
        per_page = args.get("per_page", 10)
        stmt = select(WeatherSnapshot).order_by(WeatherSnapshot.created_at.desc())
        pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)
        return [ws.to_dict() for ws in pagination.items]

from flask_smorest import Blueprint, abort
from flask.views import MethodView

from ..schemas import WeatherQuerySchema, RecommendationResponseSchema
from ..services import (
    fetch_current_weather_by_coords,
    fetch_current_weather_by_city,
    recommend_activity,
    ServiceConfigError,
)


blp = Blueprint(
    "Recommendation",
    "recommendation",
    url_prefix="/api/recommendation",
    description="Weather-based event recommendations",
)


@blp.route("/")
class Recommendation(MethodView):
    @blp.arguments(WeatherQuerySchema, location="query")
    @blp.response(200, RecommendationResponseSchema)
    def get(self, args):
        """Get weather-based recommendation.

        Provide either:
        - lat & lon
        - city (and optionally state, country)
        """
        try:
            if args.get("lat") is not None and args.get("lon") is not None:
                payload = fetch_current_weather_by_coords(args["lat"], args["lon"])
            elif args.get("city"):
                payload = fetch_current_weather_by_city(args["city"], args.get("state"), args.get("country"))
            else:
                abort(400, message="Provide either lat/lon or city (with optional state/country)")
        except ServiceConfigError as sce:
            abort(503, message=str(sce))
        except Exception as exc:
            abort(502, message=f"Weather provider error: {exc}")

        return recommend_activity(payload)

from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy import select

from ..db import db
from ..models import Event, Location, WeatherSnapshot
from ..schemas import EventSchema, PaginationSchema
from ..services import parse_iso_datetime

blp = Blueprint(
    "Events",
    "events",
    url_prefix="/api/events",
    description="Manage events with weather context",
)


@blp.route("/")
class EventsList(MethodView):
    @blp.arguments(PaginationSchema, location="query")
    @blp.response(200, EventSchema(many=True))
    def get(self, args):
        """List events with pagination"""
        page = args.get("page", 1)
        per_page = args.get("per_page", 10)
        stmt = select(Event).order_by(Event.start_time.asc())
        pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)
        return [e.to_dict() for e in pagination.items]

    @blp.arguments(EventSchema)
    @blp.response(201, EventSchema)
    def post(self, data):
        """Create a new event"""
        start_time = parse_iso_datetime(data["start_time"])
        end_time = parse_iso_datetime(data["end_time"])
        if end_time < start_time:
            abort(400, message="end_time must be after start_time")

        ev = Event(
            title=data["title"],
            description=data.get("description"),
            start_time=start_time,
            end_time=end_time,
        )

        # Optional relations
        location_id = data.get("location_id")
        if location_id:
            loc = db.session.get(Location, location_id)
            if not loc:
                abort(400, message="Invalid location_id")
            ev.location = loc

        weather_snapshot_id = data.get("weather_snapshot_id")
        if weather_snapshot_id:
            ws = db.session.get(WeatherSnapshot, weather_snapshot_id)
            if not ws:
                abort(400, message="Invalid weather_snapshot_id")
            ev.weather_snapshot = ws

        db.session.add(ev)
        db.session.commit()
        return ev.to_dict()


@blp.route("/<int:event_id>")
class EventDetail(MethodView):
    @blp.response(200, EventSchema)
    def get(self, event_id: int):
        """Get a single event"""
        ev = db.session.get(Event, event_id)
        if not ev:
            abort(404, message="Event not found")
        return ev.to_dict()

    @blp.arguments(EventSchema(partial=True))
    @blp.response(200, EventSchema)
    def patch(self, data, event_id: int):
        """Update an event"""
        ev = db.session.get(Event, event_id)
        if not ev:
            abort(404, message="Event not found")

        if "start_time" in data:
            ev.start_time = parse_iso_datetime(data["start_time"])
        if "end_time" in data:
            ev.end_time = parse_iso_datetime(data["end_time"])
        if "title" in data:
            ev.title = data["title"]
        if "description" in data:
            ev.description = data["description"]

        if "location_id" in data:
            if data["location_id"] is None:
                ev.location = None
            else:
                loc = db.session.get(Location, data["location_id"])
                if not loc:
                    abort(400, message="Invalid location_id")
                ev.location = loc

        if "weather_snapshot_id" in data:
            if data["weather_snapshot_id"] is None:
                ev.weather_snapshot = None
            else:
                ws = db.session.get(WeatherSnapshot, data["weather_snapshot_id"])
                if not ws:
                    abort(400, message="Invalid weather_snapshot_id")
                ev.weather_snapshot = ws

        if ev.end_time < ev.start_time:
            abort(400, message="end_time must be after start_time")

        db.session.commit()
        return ev.to_dict()

    @blp.response(204)
    def delete(self, event_id: int):
        """Delete an event"""
        ev = db.session.get(Event, event_id)
        if not ev:
            abort(404, message="Event not found")
        db.session.delete(ev)
        db.session.commit()
        return ""

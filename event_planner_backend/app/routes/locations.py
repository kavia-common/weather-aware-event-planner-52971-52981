from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy import select

from ..db import db
from ..models import Location
from ..schemas import LocationSchema, PaginationSchema

blp = Blueprint(
    "Locations",
    "locations",
    url_prefix="/api/locations",
    description="Manage event locations",
)


@blp.route("/")
class LocationsList(MethodView):
    @blp.arguments(PaginationSchema, location="query")
    @blp.response(200, LocationSchema(many=True))
    def get(self, args):
        """List locations with pagination."""
        page = args.get("page", 1)
        per_page = args.get("per_page", 10)
        stmt = select(Location).order_by(Location.created_at.desc())
        pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)
        return [loc.to_dict() for loc in pagination.items]

    @blp.arguments(LocationSchema)
    @blp.response(201, LocationSchema)
    def post(self, data):
        """Create a new location."""
        loc = Location(
            name=data["name"],
            city=data.get("city"),
            state=data.get("state"),
            country=data.get("country"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
        )
        db.session.add(loc)
        db.session.commit()
        return loc.to_dict()


@blp.route("/<int:location_id>")
class LocationDetail(MethodView):
    @blp.response(200, LocationSchema)
    def get(self, location_id: int):
        """Get a single location by id."""
        loc = db.session.get(Location, location_id)
        if not loc:
            abort(404, message="Location not found")
        return loc.to_dict()

    @blp.arguments(LocationSchema(partial=True))
    @blp.response(200, LocationSchema)
    def patch(self, data, location_id: int):
        """Update a location."""
        loc = db.session.get(Location, location_id)
        if not loc:
            abort(404, message="Location not found")
        for k, v in data.items():
            setattr(loc, k, v)
        db.session.commit()
        return loc.to_dict()

    @blp.response(204)
    def delete(self, location_id: int):
        """Delete a location."""
        loc = db.session.get(Location, location_id)
        if not loc:
            abort(404, message="Location not found")
        db.session.delete(loc)
        db.session.commit()
        return ""

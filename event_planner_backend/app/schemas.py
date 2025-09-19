from marshmallow import Schema, fields, validate


class LocationSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, description="Location display name")
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    created_at = fields.Str(dump_only=True)
    updated_at = fields.Str(dump_only=True)


class EventSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    start_time = fields.Str(required=True, description="ISO-8601 datetime")
    end_time = fields.Str(required=True, description="ISO-8601 datetime")
    location_id = fields.Int(load_only=True, allow_none=True)
    location = fields.Nested(LocationSchema, dump_only=True)
    weather_snapshot_id = fields.Int(load_only=True, allow_none=True)
    weather_snapshot = fields.Dict(dump_only=True)
    created_at = fields.Str(dump_only=True)
    updated_at = fields.Str(dump_only=True)


class WeatherQuerySchema(Schema):
    city = fields.Str(required=False)
    state = fields.Str(required=False)
    country = fields.Str(required=False)
    lat = fields.Float(required=False)
    lon = fields.Float(required=False)


class WeatherSnapshotSchema(Schema):
    id = fields.Int(dump_only=True)
    source = fields.Str()
    observed_at = fields.Str()
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    payload = fields.Dict()


class RecommendationResponseSchema(Schema):
    title = fields.Str()
    suggestion = fields.Str()
    style = fields.Dict()
    summary = fields.Str(allow_none=True)
    temperature = fields.Float(allow_none=True)
    precipitation = fields.Float(allow_none=True)


class PaginationSchema(Schema):
    page = fields.Int(missing=1)
    per_page = fields.Int(missing=10, validate=validate.Range(min=1, max=100))

from datetime import datetime

from .db import db


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class Location(db.Model, TimestampMixin):
    """Represents a physical or virtual event location."""
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    city = db.Column(db.String(120), nullable=True, index=True)
    state = db.Column(db.String(120), nullable=True, index=True)
    country = db.Column(db.String(120), nullable=True, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    events = db.relationship("Event", back_populates="location", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Event(db.Model, TimestampMixin):
    """Represents a planned event with optional weather association."""
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False, index=True)

    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=True)
    location = db.relationship("Location", back_populates="events")

    weather_snapshot_id = db.Column(db.Integer, db.ForeignKey("weather_snapshots.id"), nullable=True)
    weather_snapshot = db.relationship("WeatherSnapshot", back_populates="events")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "location": self.location.to_dict() if self.location else None,
            "weather_snapshot": self.weather_snapshot.to_dict() if self.weather_snapshot else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class WeatherSnapshot(db.Model, TimestampMixin):
    """Represents cached weather data for a particular datetime and geolocation."""
    __tablename__ = "weather_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    # ISO code (e.g., metric/imperial can be stored in payload)
    source = db.Column(db.String(64), nullable=True, index=True, default="openweathermap")
    observed_at = db.Column(db.DateTime, nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=True)
    country = db.Column(db.String(120), nullable=True)

    # Store raw JSON payload for flexibility
    payload = db.Column(db.JSON, nullable=True)

    events = db.relationship("Event", back_populates="weather_snapshot")

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "observed_at": self.observed_at.isoformat() if self.observed_at else None,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "payload": self.payload,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

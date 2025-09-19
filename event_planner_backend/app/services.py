import os
import requests
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Tuple


class ServiceConfigError(Exception):
    """Raised when required service configuration is missing."""


# PUBLIC_INTERFACE
def get_openweather_api_key() -> str:
    """Retrieve OpenWeatherMap API key from environment variables.

    This function checks common variable names:
    - OPENWEATHERMAP_API_KEY
    - OPENWEATHER_API_KEY
    - OWM_API_KEY

    Raises:
        ServiceConfigError: If no API key is found.
    """
    for key in ("OPENWEATHERMAP_API_KEY", "OPENWEATHER_API_KEY", "OWM_API_KEY"):
        value = os.getenv(key)
        if value:
            return value
    raise ServiceConfigError(
        "OpenWeatherMap API key is missing. Please set OPENWEATHERMAP_API_KEY in environment."
    )


def _units() -> str:
    return os.getenv("OPENWEATHERMAP_UNITS", "metric")


def _lang() -> str:
    return os.getenv("OPENWEATHERMAP_LANG", "en")


def _timeout() -> int:
    try:
        return int(os.getenv("HTTP_TIMEOUT_SECONDS", "15"))
    except Exception:
        return 15


# PUBLIC_INTERFACE
def fetch_current_weather_by_coords(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch current weather from OpenWeatherMap for given coordinates.

    Args:
        lat: Latitude
        lon: Longitude
    Returns:
        Parsed JSON dictionary from OpenWeatherMap Current Weather API.
    Raises:
        ServiceConfigError: if API key missing.
        requests.RequestException: on network/http errors.
    """
    api_key = get_openweather_api_key()
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": _units(), "lang": _lang()}
    resp = requests.get(url, params=params, timeout=_timeout())
    resp.raise_for_status()
    return resp.json()


# PUBLIC_INTERFACE
def fetch_current_weather_by_city(city: str, state: Optional[str] = None, country: Optional[str] = None) -> Dict[str, Any]:
    """Fetch current weather from OpenWeatherMap by city/state/country.

    Example: city="San Francisco", state="CA", country="US"
    """
    api_key = get_openweather_api_key()
    if state and country:
        q = f"{city},{state},{country}"
    elif country:
        q = f"{city},{country}"
    else:
        q = city
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": q, "appid": api_key, "units": _units(), "lang": _lang()}
    resp = requests.get(url, params=params, timeout=_timeout())
    resp.raise_for_status()
    return resp.json()


# PUBLIC_INTERFACE
def weather_summary(payload: Dict[str, Any]) -> Tuple[str, Optional[float], Optional[float]]:
    """Create a simplified weather summary from an OWM payload.

    Returns:
        tuple: (summary_text, temp_c_or_f, precipitation_mm)
    """
    try:
        main = payload.get("main") or {}
        weather_arr = payload.get("weather") or []
        summary = weather_arr[0]["description"] if weather_arr else "Unknown"
        temp = main.get("temp")
        precip = None
        # Precipitation may appear under "rain" or "snow" as "1h"
        if "rain" in payload and isinstance(payload["rain"], dict):
            precip = payload["rain"].get("1h") or payload["rain"].get("3h")
        if "snow" in payload and isinstance(payload["snow"], dict):
            precip = precip or payload["snow"].get("1h") or payload["snow"].get("3h")
        return summary, temp, precip
    except Exception:
        return "Unknown", None, None


# PUBLIC_INTERFACE
def recommend_activity(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Provide a simple weather-based recommendation.

    Heuristics (Ocean Professional messaging):
    - If heavy precipitation or thunderstorm: recommend indoor.
    - If clear or few clouds and temp between 10C-28C (50F-82F): outdoor recommended.
    - If very hot (>32C/90F) or very cold (<0C/32F): prefer indoor or shaded/short outdoor.
    """
    summary, temp, precip = weather_summary(payload)
    main_code = (payload.get("weather") or [{}])[0].get("id", 800)

    def msg(title: str, suggestion: str, color: str) -> Dict[str, Any]:
        return {
            "title": title,
            "suggestion": suggestion,
            "style": {"accent": "#2563EB", "highlight": "#F59E0B", "severity": color},
            "summary": summary,
            "temperature": temp,
            "precipitation": precip,
        }

    # Thunderstorm 2xx or Drizzle/Rain with measurable precipitation -> indoor
    if 200 <= main_code < 300 or (precip and precip >= 0.5):
        return msg("Stormy conditions", "Plan an indoor event or ensure covered venues.", "error")

    # Snow
    if 600 <= main_code < 700:
        return msg("Snowy weather", "Prefer cozy indoor gatherings; consider travel delays.", "error")

    # Extreme
    if temp is not None and (temp < 0 or temp > 32):
        return msg("Extreme temperatures", "Book indoor venues or schedule short outdoor activities with shade.", "error")

    # Favorable outdoor
    if 800 <= main_code < 803 and (temp is None or (10 <= temp <= 28)):
        return msg("Great outdoor conditions", "Outdoor events are recommended.", "success")

    # Default
    return msg("Mixed conditions", "Consider hybrid: outdoor with indoor fallback.", "warning")


# PUBLIC_INTERFACE
def parse_iso_datetime(value: str) -> datetime:
    """Parse an ISO-8601 datetime string to a timezone-aware UTC datetime."""
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


# PUBLIC_INTERFACE
def safe_now_utc() -> datetime:
    """Return current UTC time with timezone info."""
    return datetime.now(timezone.utc)


# PUBLIC_INTERFACE
def within_time_window(target: datetime, start: datetime, end: datetime) -> bool:
    """Return True if target lies within [start, end] inclusive."""
    return start <= target <= end

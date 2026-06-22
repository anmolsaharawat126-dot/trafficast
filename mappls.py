"""
mappls.py — thin MapmyIndia (Mappls) API client for TraffiCast AI.

External APIs (maps / routing / geocoding) are explicitly permitted by the
hackathon admin. They are used at DISPLAY / inference time only — NOT as training
data — so they do not violate the "provided dataset only" rule.

Auth: set ONE of these (env var or st.secrets):
  - MAPPLS_REST_KEY      → used in the advancedmaps URL (simplest)
  - MAPPLS_CLIENT_ID + MAPPLS_CLIENT_SECRET → OAuth token flow (for some products)

Every function fails SAFE: if no key / network error, it returns None and the
UI falls back to a straight-line placeholder so the demo never breaks.
"""
from __future__ import annotations
import os, time, math
import requests

_TOKEN_CACHE = {"token": None, "exp": 0}


def _get(name, default=None):
    val = os.environ.get(name)
    if val:
        return val
    try:                       # allow keys via Streamlit secrets — but ONLY if a secrets
        import streamlit as st  # file actually exists, else Streamlit prints a noisy warning
        paths = [os.path.expanduser("~/.streamlit/secrets.toml"),
                 os.path.join(os.getcwd(), ".streamlit", "secrets.toml")]
        if any(os.path.exists(p) for p in paths):
            return st.secrets.get(name, default)
    except Exception:
        pass
    return default


def has_key() -> bool:
    return bool(_get("MAPPLS_REST_KEY") or (_get("MAPPLS_CLIENT_ID") and _get("MAPPLS_CLIENT_SECRET")))


def _oauth_token():
    cid, secret = _get("MAPPLS_CLIENT_ID"), _get("MAPPLS_CLIENT_SECRET")
    if not (cid and secret):
        return None
    if _TOKEN_CACHE["token"] and _TOKEN_CACHE["exp"] > time.time() + 30:
        return _TOKEN_CACHE["token"]
    try:
        r = requests.post("https://outpost.mappls.com/api/security/oauth/token",
                          data={"grant_type": "client_credentials",
                                "client_id": cid, "client_secret": secret}, timeout=10)
        j = r.json()
        _TOKEN_CACHE["token"] = j["access_token"]
        _TOKEN_CACHE["exp"] = time.time() + int(j.get("expires_in", 3600))
        return _TOKEN_CACHE["token"]
    except Exception:
        return None


def directions(origin, dest, alternatives=3):
    """origin/dest = (lat, lon). Returns list of routes:
       [{'coords': [(lat,lon),...], 'distance_km': float, 'duration_min': float}] or None."""
    key = _get("MAPPLS_REST_KEY")
    olat, olon = origin; dlat, dlon = dest
    # Mappls advancedmaps Route Adv API (lng,lat;lng,lat order)
    if key:
        url = (f"https://apis.mappls.com/advancedmaps/v1/{key}/route_adv/driving/"
               f"{olon},{olat};{dlon},{dlat}")
        params = {"geometries": "geojson", "overview": "full",
                  "alternatives": str(alternatives)}
        try:
            r = requests.get(url, params=params, timeout=12)
            data = r.json()
            routes = []
            for rt in data.get("routes", []):
                geo = rt.get("geometry", {}).get("coordinates", [])
                routes.append({
                    "coords": [(c[1], c[0]) for c in geo],          # -> (lat,lon)
                    "distance_km": round(rt.get("distance", 0)/1000, 2),
                    "duration_min": round(rt.get("duration", 0)/60, 1)})
            if routes:
                return routes
        except Exception:
            pass
    return None


def reverse_geocode(lat, lon):
    key = _get("MAPPLS_REST_KEY")
    if not key:
        return None
    try:
        r = requests.get(f"https://apis.mappls.com/advancedmaps/v1/{key}/rev_geocode",
                         params={"lat": lat, "lng": lon}, timeout=10)
        res = r.json().get("results", [])
        return res[0].get("formatted_address") if res else None
    except Exception:
        return None


def geocode(address):
    key = _get("MAPPLS_REST_KEY")
    if not key:
        return None
    try:
        r = requests.get(f"https://apis.mappls.com/advancedmaps/v1/{key}/geocode",
                         params={"address": address}, timeout=10)
        c = r.json().get("copResults") or (r.json().get("results") or [None])[0]
        if c:
            return (float(c["latitude"]), float(c["longitude"]))
    except Exception:
        pass
    return None


def haversine_km(a, b):
    (la1, lo1), (la2, lo2) = a, b
    R = 6371.0
    dlat = math.radians(la2-la1); dlon = math.radians(lo2-lo1)
    h = (math.sin(dlat/2)**2 + math.cos(math.radians(la1))*math.cos(math.radians(la2))*math.sin(dlon/2)**2)
    return 2*R*math.asin(math.sqrt(h))


def route_min_distance_to(route_coords, point):
    """Closest approach (km) of a route to a point — higher = better diversion (avoids it)."""
    if not route_coords:
        return 0.0
    return min(haversine_km(c, point) for c in route_coords)

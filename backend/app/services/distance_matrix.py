import math
from typing import Dict, Tuple
from app.models.farm import Coordinates

def haversine_distance_km(coord1: Coordinates, coord2: Coordinates) -> float:
    """Calculate the great-circle distance between two points in km."""
    R = 6371.0  # Earth radius in kilometers
    lat1, lon1 = math.radians(coord1.lat), math.radians(coord1.lng)
    lat2, lon2 = math.radians(coord2.lat), math.radians(coord2.lng)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def calculate_travel_time_hours(coord1: Coordinates, coord2: Coordinates, avg_speed_kmh: float = 25.0) -> float:
    """
    Calculate tractor/baler transit time in hours between two coordinates.
    Includes a 10-minute (0.16 hr) field positioning buffer.
    """
    dist_km = haversine_distance_km(coord1, coord2)
    if dist_km < 0.2:
        return 0.1  # Negligible adjacent field movement
    drive_time = dist_km / avg_speed_kmh
    return round(drive_time + 0.16, 2)

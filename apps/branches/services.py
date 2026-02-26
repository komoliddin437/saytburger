from typing import Optional

from .models import Branch


def get_nearest_branch(lat: float, lon: float) -> Optional[tuple[Branch, float]]:
    candidates = Branch.objects.filter(is_active=True).only(
        "id", "name", "latitude", "longitude", "delivery_radius_km", "address", "phone"
    )
    nearest = None
    nearest_distance = None
    for branch in candidates:
        distance = branch.distance_km(lat, lon)
        if nearest_distance is None or distance < nearest_distance:
            nearest = branch
            nearest_distance = distance
    if nearest is None:
        return None
    return nearest, float(nearest_distance)

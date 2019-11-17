from src.marker import marker_db
from src.marker.rect_marker import RectMarker
from src.marker.interpolated_marker import InterpolatedMarker

marker_db.add_marker_class(RectMarker)
marker_db.add_marker_class(InterpolatedMarker)

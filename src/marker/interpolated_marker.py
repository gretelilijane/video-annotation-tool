import numpy as np

from src.marker.marker_db import get_marker_by_id
from src.marker.rect_marker import RectMarker


class InterpolatedMarker(RectMarker):
    DB_TABLE = "interpolated_markers"
    DB_COLUMNS = { "src_marker_table": "TEXT", "src_marker_id": "INTEGER", "dst_marker_table": "TEXT", "dst_marker_id": "INTEGER" }

    def init(self, src_marker_table, src_marker_id, dst_marker_table, dst_marker_id):
        self.highlighted_edge = (None, None)

        self.src = get_marker_by_id(src_marker_table, src_marker_id)
        self.dst = get_marker_by_id(dst_marker_table, dst_marker_id)

    def get_db_values(self):
        return (self.src.DB_TABLE, self.src.id, self.dst.DB_TABLE, self.dst.id)

    def get_coords(self):
        src_coords = self.src.get_coords()
        dst_coords = self.dst.get_coords()
        coords = src_coords + (self.frame - self.src.frame) / (self.dst.frame - self.src.frame) * (dst_coords - src_coords)

        return coords.astype(np.int)

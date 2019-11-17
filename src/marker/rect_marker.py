import cv2
import numpy as np

from src import SELECT_EDGE_DISTANCE, COLORS
from src.marker.base_marker import BaseMarker


class RectMarker(BaseMarker):
    DB_TABLE = "rect_markers"
    DB_COLUMNS = { "x_min": "INTEGER", "y_min": "INTEGER", "x_max": "INTEGER", "y_max": "INTEGER" }

    def init(self, *coords):
        self.highlighted_edge = (None, None)
        self.set_coords(coords)

    def get_db_values(self):
        return self.get_coords().tolist()

    def contains_coord(self, c):
        coords = self.get_coords()
        return c[0] >= coords[0] and c[0] <= coords[2] and c[1] >= coords[1] and c[1] <= coords[3]

    def get_closest_edge(self, c):
        coords = self.get_coords()

        in_horizontally = c[0] > coords[0] - SELECT_EDGE_DISTANCE and c[0] < coords[2] + SELECT_EDGE_DISTANCE
        in_vertically = c[1] > coords[1] - SELECT_EDGE_DISTANCE and c[1] < coords[3] + SELECT_EDGE_DISTANCE

        dist = list(map(lambda i: abs(c[i % 2] - coords[i]), range(4)))
        edge = [None, None]

        if in_vertically:
            if dist[0] < SELECT_EDGE_DISTANCE and dist[0] <= dist[2]:
                edge[0] = 0
            elif dist[2] < SELECT_EDGE_DISTANCE and dist[2] <= dist[0]:
                edge[0] = 2

        if in_horizontally:
            if dist[1] < SELECT_EDGE_DISTANCE and dist[1] <= dist[3]:
                edge[1] = 1
            elif dist[3] < SELECT_EDGE_DISTANCE and dist[3] <= dist[1]:
                edge[1] = 3

        return tuple(edge)

    def get_coords(self):
        return self.coords

    def set_coords(self, coords):
        self.coords = np.array((
            min(coords[0], coords[2]),
            min(coords[1], coords[3]),
            max(coords[0], coords[2]),
            max(coords[1], coords[3])
        ), dtype=int)

    def highlight_edge(self, edge):
        self.highlighted_edge = edge
    
    def is_highlighted(self):
        return self.highlighted_edge[0] is not None or self.highlighted_edge[1] is not None

    def draw(self, frame):
        color = COLORS[(self.label_id - 1) % len(COLORS)]
        coords = self.get_coords()
        cv2.rectangle(frame, tuple(coords[0:2]), tuple(coords[2:4]), color)

        if self.highlighted_edge[0] is not None:
            cv2.line(frame,
                (coords[self.highlighted_edge[0]], coords[1]),
                (coords[self.highlighted_edge[0]], coords[3]),
                color, thickness=3)

        if self.highlighted_edge[1] is not None:
            cv2.line(frame,
                (coords[0], coords[self.highlighted_edge[1]]),
                (coords[2], coords[self.highlighted_edge[1]]),
                color, thickness=3)

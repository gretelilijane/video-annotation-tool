import cv2
import numpy as np

from src.marker.db_marker import DbMarker
from src.constants import SELECT_EDGE_DISTANCE, db_cur


class RectMarker(DbMarker):
    DB_PARAMS = ("x_min", "y_min", "x_max", "y_max")

    def __init__(self, frame, label, coords):
        super().__init__(frame, label)
        self.highlighted_edge = (None, None)
        self.set_coords(coords)

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
        coords = self.get_coords()
        cv2.rectangle(frame, tuple(coords[0:2]), tuple(coords[2:4]), (255, 0, 0))

        if self.highlighted_edge[0] is not None:
            cv2.line(frame,
                (coords[self.highlighted_edge[0]], coords[1]),
                (coords[self.highlighted_edge[0]], coords[3]),
                (255, 0, 0), thickness=3)

        if self.highlighted_edge[1] is not None:
            cv2.line(frame,
                (coords[0], coords[self.highlighted_edge[1]]),
                (coords[2], coords[self.highlighted_edge[1]]),
                (255, 0, 0), thickness=3)

    def get_db_params(self):
        return self.coords.tolist()

    @staticmethod
    def findall(frame):
        markers = []
        db_cur.execute("SELECT * FROM rect_markers WHERE frame=?", (frame, ))

        for row in db_cur.fetchall():
            markers.append(RectMarker(frame, row[1], row[2:6]))

        return markers

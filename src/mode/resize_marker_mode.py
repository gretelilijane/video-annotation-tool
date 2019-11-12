import cv2

from src.mode.default_mode import DefaultMode
from src.constants import db


class ResizeMarkerMode(DefaultMode):
    def __init__(self, state, marker):
        self.state = state
        self.marker = marker
        self.new_coords = [None, None, None, None]

        if marker.highlighted_edge[0] is None or marker.highlighted_edge[0] == 0:
            self.new_coords[2] = marker.coords[2]

        if marker.highlighted_edge[0] is None or marker.highlighted_edge[0] == 2:
            self.new_coords[0] = marker.coords[0]

        if marker.highlighted_edge[1] is None or marker.highlighted_edge[1] == 1:
            self.new_coords[3] = marker.coords[3]

        if marker.highlighted_edge[1] is None or marker.highlighted_edge[1] == 3:
            self.new_coords[1] = marker.coords[1]

    def on_mousemove(self):
        coords = []

        for i, coord in enumerate(self.new_coords):
            if coord is None:
                coords.append(self.state.mouse[i % 2])
            else:
                coords.append(coord)

        self.marker.set_coords(coords)
        self.state.draw_frame()

    def on_lbuttonup(self):
        self.state.enter_default_mode()

    def draw_frame(self, frame):
        self.marker.draw(frame)

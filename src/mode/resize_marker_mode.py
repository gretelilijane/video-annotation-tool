import cv2

from src.mode.default_mode import DefaultMode
from src.marker import Marker


class ResizeMarkerMode(DefaultMode):
    def __init__(self, state, marker, edge):
        self.state = state
        self.marker = marker
        self.edge = edge
        self.new_coords = []

        # Use y-axis if the x-coords of the edge coordinates are different, x-axis otherwise
        if edge[0][0] == edge[1][0]:
            self.change_axis = 0
            self.fixed_axis = 1
        else:
            self.change_axis = 1
            self.fixed_axis = 0

        self.edge_indices = list(filter(lambda p: p[1] in edge, enumerate((marker.p1, marker.p2, marker.p3, marker.p4))))

    def on_mousemove(self, c):
        for coord in self.edge_indices:
            if self.change_axis:
                new_coord = (coord[1][self.fixed_axis], c[self.change_axis])
            else: 
                new_coord = (c[self.change_axis], coord[1][self.fixed_axis])

            self.marker.update_coord(coord[0], new_coord)

        self.state.draw_frame()

    def on_lbuttonup(self, c):
        self.state.enter_default_mode()
        self.state.draw_frame()

    def draw_frame(self, frame):
        self.marker.draw(frame)

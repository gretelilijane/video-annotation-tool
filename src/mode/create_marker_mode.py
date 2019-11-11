import cv2

from src.mode.default_mode import DefaultMode
from src.marker import Marker


class CreateMarkerMode(DefaultMode):
    def __init__(self, state, c):
        self.state = state
        self.origin = c

    def on_lbuttondown(self, c, flags):
        self.state.add_marker(Marker(self.state.label, (*self.origin, *c)))
        self.state.enter_default_mode()

    def draw_frame(self, frame):
        super().draw_frame(frame)
        Marker(self.state.label, (*self.origin, *self.state.mouse)).draw(frame)

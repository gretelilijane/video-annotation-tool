import cv2

from src.mode.default_mode import DefaultMode
from src.marker.rect_marker import RectMarker


class CreateMarkerMode(DefaultMode):
    def __init__(self, state):
        self.state = state
        self.origin = self.state.mouse

    def on_lbuttonup(self):
        if self.state.mouse != self.origin:
            marker = RectMarker(None, self.state.frame, self.state.get_selected_label_id(), 1, *self.origin, *self.state.mouse)
            marker.save()

            self.state.add_marker(marker)

        self.state.enter_default_mode()

    def draw_frame(self, frame):
        super().draw_frame(frame)
        RectMarker(None, self.state.frame, self.state.get_selected_label_id(), 0, *self.origin, *self.state.mouse).draw(frame)

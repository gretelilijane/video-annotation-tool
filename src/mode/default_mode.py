import cv2

from src.constants import IMAGE_SIZE


class DefaultMode:
    def __init__(self, state):
        self.state = state

    def on_mousemove(self, c):
        self.state.draw_frame()

        for marker in self.state.get_markers():
            edge = marker.get_closest_edge(c)
            marker.highlight_edge(edge)

    def on_lbuttondown(self, c, flags):
        # Ctrl + mousedown
        if flags & cv2.EVENT_FLAG_CTRLKEY:
            for marker in self.state.get_markers():
                if marker.contains_coord(c):
                    self.state.remove_marker(marker)
                    break
            return

        # Mousedown
        highlighted_markers = list(filter(lambda marker: marker.highlighted_edge != None, self.state.get_markers()))

        if len(highlighted_markers):
            self.state.enter_resize_marker_mode(highlighted_markers[0])
            highlighted_markers[0].highlight_edge(None)
            return

        self.state.enter_create_marker_mode(c)

    def on_lbuttonup(self, c):
        pass

    def draw_frame(self, frame):
        if self.state.mouse is not None:
            cv2.line(frame, (self.state.mouse[0], 0), (self.state.mouse[0], IMAGE_SIZE[1]), (0, 0, 255))
            cv2.line(frame, (0, self.state.mouse[1]), (IMAGE_SIZE[0], self.state.mouse[1]), (0, 0, 255))

        for marker in self.state.get_markers():
            marker.draw(frame)


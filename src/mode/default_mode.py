import cv2

from src import WINDOW_NAME, FRAME_TRACKBAR_NAME, FRAME_COUNT, IMAGE_SIZE, COLORS


class DefaultMode:
    def __init__(self, state):
        self.state = state

    def on_mousemove(self):
        self.state.draw_frame()

        for marker in self.state.get_markers():
            edge = marker.get_closest_edge(self.state.mouse)
            marker.highlight_edge(edge)

    def on_lbuttondown(self, flags):
        # Ctrl + mousedown
        if flags & cv2.EVENT_FLAG_CTRLKEY:
            for marker in self.state.get_markers():
                if marker.contains_coord(self.state.mouse):
                    marker.remove()
                    self.state.remove_marker(marker)
                    break
            return

        # Mousedown
        highlighted_markers = list(filter(lambda marker: marker.is_highlighted(), self.state.get_markers()))

        if len(highlighted_markers):
            self.state.enter_resize_marker_mode(highlighted_markers[0])
            highlighted_markers[0].highlight_edge((None, None))
            return

        self.state.enter_create_marker_mode()

    def on_lbuttonup(self):
        pass

    def on_key(self, key):
        if key == 97 and self.state.frame > 0:
            self.state.set_frame(self.state.frame - 1)
        elif key == 100 and self.state.frame < FRAME_COUNT - 1:
            self.state.set_frame(self.state.frame + 1)
        elif key == ord("t") and self.state.frame < FRAME_COUNT - 1:
            self.state.enter_track_mode()
        elif key == ord("c"):
            for marker in self.state.get_markers():
                marker.remove()

            self.state.markers = []
            self.state.draw_frame()

    def draw_frame(self, frame):
        if self.state.mouse is not None:
            selected_label_color = COLORS[(self.state.get_selected_label_id() - 1) % len(COLORS)]
            cv2.line(frame, (self.state.mouse[0], 0), (self.state.mouse[0], IMAGE_SIZE[1]), selected_label_color)
            cv2.line(frame, (0, self.state.mouse[1]), (IMAGE_SIZE[0], self.state.mouse[1]), selected_label_color)

        for marker in self.state.get_markers():
            marker.draw(frame)

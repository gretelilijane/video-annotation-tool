import cv2

from src.mode.default_mode import DefaultMode
from src.track import create_tracker
from src.marker.rect_marker import RectMarker
from src.marker.interpolated_marker import InterpolatedMarker
from src.constants import TRACKER_NAME


class TrackMode(DefaultMode):
    def __init__(self, state):
        self.state = state

        src_frame = state.frame
        src_markers = state.get_markers()
        trackers = []

        for marker in src_markers:
            tracker = create_tracker(TRACKER_NAME)
            tracker.init(state.image, marker.get_coords())
            trackers.append(tracker)

        state.set_frame(state.frame + 10)

        for i in range(len(src_markers)):
            coords = trackers[i].update(state.image)
            dst_marker = RectMarker(state.frame, src_markers[i].label, coords)
            state.add_marker(dst_marker)

            for j in range(1, 10):
                state.add_marker(InterpolatedMarker(src_frame + j, src_markers[i].label, src_markers[i], dst_marker))

        state.enter_default_mode()

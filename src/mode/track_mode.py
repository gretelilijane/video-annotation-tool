import cv2

from src.mode.default_mode import DefaultMode
from src.track import create_tracker
from src.marker.rect_marker import RectMarker
from src.marker.interpolated_marker import InterpolatedMarker
from src.constants import TRACKER_NAME, TRACKER_FRAME_SKIP


class TrackMode(DefaultMode):
    def __init__(self, state):
        self.state = state

        src_frame = state.frame
        src_markers = list(filter(lambda marker: marker.trackable, state.get_markers()))
        trackers = []

        for marker in src_markers:
            tracker = create_tracker(TRACKER_NAME)
            tracker.init(state.image, marker.get_coords())
            trackers.append(tracker)
            marker.set_untrackable()

        state.set_frame(state.frame + TRACKER_FRAME_SKIP)

        for i in range(len(src_markers)):
            coords = trackers[i].update(state.image)
            dst_marker = RectMarker(None, state.frame, src_markers[i].label_id, 1, *coords)
            dst_marker.save()
            state.add_marker(dst_marker)

            for j in range(1, TRACKER_FRAME_SKIP):
                m = InterpolatedMarker(None, src_frame + j, src_markers[i].label_id, 0, src_markers[i].DB_TABLE, src_markers[i].id, dst_marker.DB_TABLE, dst_marker.id)
                m.save()

        state.enter_default_mode()

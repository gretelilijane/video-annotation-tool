import cv2
import numpy as np

from src.marker.rect_marker import RectMarker


class InterpolatedMarker(RectMarker):
    def __init__(self, frame, label, src_marker, dst_marker):
        self.frame = frame
        self.label = label
        self.highlighted_edge = (None, None)
        self.src = src_marker
        self.dst = dst_marker

    def get_coords(self):
        src_coords = self.src.get_coords()
        dst_coords = self.dst.get_coords()
        coords = src_coords + (self.frame - self.src.frame) / (self.dst.frame - self.src.frame) * (dst_coords - src_coords)

        return coords.astype(np.int)

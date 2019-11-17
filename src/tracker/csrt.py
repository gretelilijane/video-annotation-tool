import cv2
import numpy as np


class CSRTTracker:
    def __init__(self):
        self.tracker = cv2.TrackerCSRT_create()

    def init(self, image, coords):
        self.tracker.init(image, (coords[0], coords[1], coords[2] - coords[0], coords[3] - coords[1]))

    def update(self, image):
        success, bbox = self.tracker.update(image)

        if not success:
            return None

        return (
            bbox[0], bbox[1],
            bbox[0] + bbox[2], bbox[1] + bbox[3]
        )

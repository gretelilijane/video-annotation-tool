import cv2
import os
import numpy as np

from src.mode.default_mode import DefaultMode
from src.mode.create_marker_mode import CreateMarkerMode
from src.mode.resize_marker_mode import ResizeMarkerMode
from src.mode.track_mode import TrackMode
from src.marker.rect_marker import RectMarker
from src.constants import *


class State:
    image = None
    mouse = None
    markers = []
    frame = None
    label = 1
    mode = None

    @staticmethod
    def get_markers():
        return State.markers

    @staticmethod
    def add_marker(marker):
        State.markers.append(marker)

        if marker.frame == State.frame:
            State.draw_frame()

    @staticmethod
    def remove_marker(marker):
        State.markers.remove(marker)

        if marker.frame == State.frame:
            State.draw_frame()

    @staticmethod
    def draw_frame():
        frame = State.image.copy()
        State.mode.draw_frame(frame)
        cv2.imshow(WINDOW_NAME, frame)

    @staticmethod
    def set_frame(frame):
        cv2.setTrackbarPos(FRAME_TRACKBAR_NAME, WINDOW_NAME, frame)

    @staticmethod
    def set_frame_from_trackbar(frame):
        State.frame = frame
        State.image = cv2.imread(os.path.join(FRAMES_PATH, str(State.frame) + ".jpg"))
        State.markers = RectMarker.findall(State.frame)
        State.draw_frame()

    @staticmethod
    def on_mouse(event, x, y, flags, param):
        State.mouse = (x, y)

        if event == cv2.EVENT_MOUSEMOVE:
            State.mode.on_mousemove()
        elif event == cv2.EVENT_LBUTTONDOWN:
            State.mode.on_lbuttondown(flags)
        elif event == cv2.EVENT_LBUTTONUP:
            State.mode.on_lbuttonup()

    @staticmethod
    def on_key(key):
        State.mode.on_key(key)

    @staticmethod
    def enter_default_mode():
        State.mode = DefaultMode(State)

    @staticmethod
    def enter_create_marker_mode():
        State.mode = CreateMarkerMode(State)

    @staticmethod
    def enter_resize_marker_mode(marker):
        State.mode = ResizeMarkerMode(State, marker)

    @staticmethod
    def enter_track_mode():
        State.mode = TrackMode(State)


# Set up UI
cv2.namedWindow(WINDOW_NAME)
cv2.createTrackbar("Frame", WINDOW_NAME, 0, FRAMES - 1, State.set_frame_from_trackbar)
cv2.setMouseCallback(WINDOW_NAME, State.on_mouse)


# Initialize state
State.enter_default_mode()
State.set_frame_from_trackbar(0)


# Event loop
while True:
    key = cv2.waitKey(10)

    if key != -1:
        State.on_key(key)

    if key == ord("q"):
        break

db.close()

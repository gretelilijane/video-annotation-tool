import cv2
import os
import numpy as np

from src import db
from src.mode.default_mode import DefaultMode
from src.mode.create_marker_mode import CreateMarkerMode
from src.mode.resize_marker_mode import ResizeMarkerMode
from src.mode.track_mode import TrackMode
from src.marker.marker_db import get_markers_on_frame
from src import *


class State:
    image = None
    mouse = None
    markers = []
    frame = None
    label = 0
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
    def get_label_display():
        label_width = int(IMAGE_SIZE[0] / len(LABELS))
        img = np.zeros((LABEL_DISPLAY_HEIGHT, 0, 3), dtype=np.uint8)

        for i in range(len(LABELS)):
            width = label_width if i > 0 else label_width + IMAGE_SIZE[0] % label_width
            thickness = 1 if i != State.label else 2
            text = str(i + 1) + ". " + LABELS[i][1]
            text_size, baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, thickness)

            label_display = np.zeros((LABEL_DISPLAY_HEIGHT, width, 3), dtype=np.uint8)
            label_display[:,:,0] = np.ones((LABEL_DISPLAY_HEIGHT, width), dtype=np.uint8) * COLORS[i % len(COLORS)][0]
            label_display[:,:,1] = np.ones((LABEL_DISPLAY_HEIGHT, width), dtype=np.uint8) * COLORS[i % len(COLORS)][1]
            label_display[:,:,2] = np.ones((LABEL_DISPLAY_HEIGHT, width), dtype=np.uint8) * COLORS[i % len(COLORS)][2]

            img = np.concatenate((img, label_display), axis=1)
            cv2.putText(img, text, (i*width + width//2 - text_size[0]//2, LABEL_DISPLAY_HEIGHT//2 + baseline), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness)

        return img

    @staticmethod
    def get_selected_label_id():
        return LABELS[State.label][0]

    @staticmethod
    def draw_frame():
        frame = State.image.copy()
        State.mode.draw_frame(frame)
        frame = np.concatenate((frame, State.get_label_display()), axis=0)
        cv2.imshow(WINDOW_NAME, frame)

    @staticmethod
    def set_frame(frame):
        cv2.setTrackbarPos(FRAME_TRACKBAR_NAME, WINDOW_NAME, frame)

    @staticmethod
    def set_frame_from_trackbar(frame):
        State.frame = frame

        db.execute("SELECT data FROM images WHERE asset_id=? AND frame=?", (ASSET_ID, State.frame))
        row = db.fetchone()

        State.image = cv2.imdecode(np.frombuffer(row[0], np.uint8), cv2.IMREAD_UNCHANGED)
        State.markers = get_markers_on_frame(State.frame)
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
cv2.createTrackbar("Frame", WINDOW_NAME, 0, FRAME_COUNT - 1, State.set_frame_from_trackbar)
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
    elif key >= 49 and key < 57:
        label_index = key - 49

        if label_index < len(LABELS):
            State.label = label_index
            State.draw_frame()

db.close()

import cv2
import os
import configparser
import numpy as np

from src.track import create_tracker
from src.marker import Marker
from src.mode.default_mode import DefaultMode
from src.mode.create_marker_mode import CreateMarkerMode
from src.mode.resize_marker_mode import ResizeMarkerMode
from src.constants import *


# Initialize output directory
try:
    os.makedirs(FRAMES_PATH)

    # Extract all frames and save separately as images
    video = cv2.VideoCapture(args.input)
    frame_number = 0

    while video.isOpened():
        success, frame = video.read()
        if not success:
            break

        frame = cv2.resize(frame, IMAGE_SIZE)
        cv2.imwrite(os.path.join(FRAMES_PATH, str(frame_number) + ".jpg"), frame)
        frame_number += 1
        print(frame_number)

    # Write about ini file
    about = configparser.ConfigParser()
    about["DEFAULT"] = {
        "frames": frame_number,
        "width": IMAGE_SIZE[0],
        "height": IMAGE_SIZE[1]
    }
    
    with open(ABOUT_PATH, "w") as about_file:
        about.write(about_file)

except FileExistsError:
    pass


# Read config
about = configparser.ConfigParser()
about.read(ABOUT_PATH)
FRAMES = int(about["DEFAULT"]["frames"])


class State:
    image = None
    mouse = None
    markers = [[] for i in range(FRAMES)]
    frame = None
    label = 1
    mode = None

    @staticmethod
    def get_markers():
        return State.markers[State.frame]
    
    @staticmethod
    def add_marker(marker):
        State.get_markers().append(marker)
        State.draw_frame()
    
    @staticmethod
    def remove_marker(marker):
        State.get_markers().remove(marker)
        State.draw_frame()

    @staticmethod
    def draw_frame():
        frame = State.image.copy()
        State.mode.draw_frame(frame)
        cv2.imshow(WINDOW_NAME, frame)

    @staticmethod
    def set_frame(value):
        State.frame = value
        State.image = cv2.imread(os.path.join(FRAMES_PATH, str(value) + ".jpg"))
        State.draw_frame()

    @staticmethod
    def on_mouse(event, x, y, flags, param):
        State.mouse = (x, y)

        if event == cv2.EVENT_MOUSEMOVE:
            State.mode.on_mousemove(State.mouse)
        elif event == cv2.EVENT_LBUTTONDOWN:
            State.mode.on_lbuttondown(State.mouse, flags)
        elif event == cv2.EVENT_LBUTTONUP:
            State.mode.on_lbuttonup(State.mouse)

    @staticmethod
    def enter_default_mode():
        State.mode = DefaultMode(State)
        State.mode.on_mousemove

    @staticmethod
    def enter_create_marker_mode(c):
        State.mode = CreateMarkerMode(State, c)
    
    @staticmethod
    def enter_resize_marker_mode(marker):
        State.mode = ResizeMarkerMode(State, marker, marker.highlighted_edge)


cv2.namedWindow(WINDOW_NAME)
cv2.createTrackbar("Frame", WINDOW_NAME, 0, FRAMES - 1, State.set_frame)
cv2.setMouseCallback(WINDOW_NAME, State.on_mouse)

# Initialize state
State.enter_default_mode()
State.set_frame(0)

# Event loop
while True:
    key = cv2.waitKey(10)

    if key != -1:
        print("keycode:", key)

    if key == ord("q"):
        break
    elif key == 97 and State.frame > 0:
        cv2.setTrackbarPos("Frame", WINDOW_NAME, State.frame - 1)
    elif key == 100 and State.frame < FRAMES - 1:
        cv2.setTrackbarPos("Frame", WINDOW_NAME, State.frame + 1)


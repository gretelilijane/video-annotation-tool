import cv2
import argparse
import os
import configparser
import numpy as np

from src.track import create_tracker
from src.marker import Marker


parser = argparse.ArgumentParser()
parser.add_argument("--input")
parser.add_argument("--output", default="output/")
parser.add_argument("--resize", default="1280x720")
parser.add_argument("--tracker", default="dasiamrpn")
args = parser.parse_args()

# Constants
WINDOW_NAME = "Video annotation tool"
INPUT_FILE_NAME = os.path.split(args.input)[1]
ABOUT_PATH = os.path.join(args.output, INPUT_FILE_NAME, "about.ini")
FRAMES_PATH = os.path.join(args.output, INPUT_FILE_NAME, "frames")
IMAGE_SIZE = tuple([int(size) for size in args.resize.split("x")])
TRACKER_NAME = args.tracker


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


class DefaultMode:
    def on_mousemove(self, c):
        State.mouse = c
        State.draw_frame()

        for marker in State.get_markers():
            edge = marker.get_closest_edge(c)
            marker.highlight_edge(edge)

    def on_lbuttondown(self, c, flags):
        # Ctrl + mousedown
        if flags & cv2.EVENT_FLAG_CTRLKEY:
            for marker in State.get_markers():
                if marker.contains_coord(c):
                    State.remove_marker(marker)
                    break
            return

        # Mousedown
        highlighted_markers = list(filter(lambda marker: marker.highlighted_edge != None, State.get_markers()))

        if len(highlighted_markers):
            marker = highlighted_markers[0]
            State.mode = ResizeMarkerMode(marker, marker.highlighted_edge)
            return

        State.mode = CreateMarkerMode(c)

    def on_lbuttonup(self, c):
        pass

    def draw_frame(self, frame):
        if State.mouse is not None:
            cv2.line(frame, (State.mouse[0], 0), (State.mouse[0], IMAGE_SIZE[1]), (0, 0, 255))
            cv2.line(frame, (0, State.mouse[1]), (IMAGE_SIZE[0], State.mouse[1]), (0, 0, 255))

        for marker in State.get_markers():
            marker.draw(frame)


class CreateMarkerMode(DefaultMode):
    def __init__(self, c):
        self.origin = c

    def on_lbuttondown(self, c, flags):
        State.add_marker(Marker(State.label, (*self.origin, *c)))
        State.mode = DefaultMode()

    def draw_frame(self, frame):
        super().draw_frame(frame)
        Marker(State.label, (*self.origin, *State.mouse)).draw(frame)


class ResizeMarkerMode(DefaultMode):
    def __init__(self, marker, edge):
        self.marker = marker
        self.edge = edge
        self.new_coords = []

        # Use y-axis if the x-coords of the edge coordinates are different, x-axis otherwise
        if edge[0][0] == edge[1][0]:
            self.change_axis = 0
            self.fixed_axis = 1
        else:
            self.change_axis = 1
            self.fixed_axis = 0

        self.edge_indices = list(filter(lambda p: p[1] in edge, enumerate((marker.p1, marker.p2, marker.p3, marker.p4))))

    def on_mousemove(self, c):
        for coord in self.edge_indices:
            if self.change_axis:
                new_coord = (coord[1][self.fixed_axis], c[self.change_axis])
            else: 
                new_coord = (c[self.change_axis], coord[1][self.fixed_axis])

            self.marker.update_coord(coord[0], new_coord)

        State.draw_frame()

    def on_lbuttonup(self, c):
        State.mode = DefaultMode()
        State.draw_frame()
    
    def draw_frame(self, frame):
        self.marker.draw(frame)


class State:
    image = None
    mouse = None
    markers = [[] for i in range(FRAMES)]
    frame = None
    label = 1
    mode = DefaultMode()

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
        cv2.EVENT_FLAG_CTRLKEY
        if event == cv2.EVENT_MOUSEMOVE:
            State.mode.on_mousemove((x, y))
        elif event == cv2.EVENT_LBUTTONDOWN:
            State.mode.on_lbuttondown((x, y), flags)
        elif event == cv2.EVENT_LBUTTONUP:
            State.mode.on_lbuttonup((x, y))


cv2.namedWindow(WINDOW_NAME)
cv2.createTrackbar("Frame", WINDOW_NAME, 0, FRAMES - 1, State.set_frame)
cv2.setMouseCallback(WINDOW_NAME, State.on_mouse)
State.set_frame(0)

# Event loop
while True:
    key = cv2.waitKey(10)

    if key != -1:
        print(key)

    if key == ord("q"):
        break
    elif key == 97 and State.frame > 0:
        print("set it ", State.frame - 1)
        cv2.setTrackbarPos("Frame", WINDOW_NAME, State.frame - 1)
    elif key == 100 and State.frame < FRAMES - 1:
        print("set it ", State.frame + 1)
        cv2.setTrackbarPos("Frame", WINDOW_NAME, State.frame + 1)


import cv2
import argparse
import os
import configparser


parser = argparse.ArgumentParser()
parser.add_argument("--input")
parser.add_argument("--output", default="output/")
parser.add_argument("--resize", default="1280x720")
args = parser.parse_args()

# Constants
WINDOW_NAME = "Video annotation tool"
INPUT_FILE_NAME = os.path.split(args.input)[1]
ABOUT_PATH = os.path.join(args.output, INPUT_FILE_NAME, "about.ini")
FRAMES_PATH = os.path.join(args.output, INPUT_FILE_NAME, "frames")
IMAGE_SIZE = tuple([int(size) for size in args.resize.split("x")])
SELECT_EDGE_DISTANCE = 10


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


class Marker:
    def __init__(self, label, coords):
        self.label = label
        self.highlighted_edge = None
        self.set_coords(coords)

    def contains_coord(self, c):
        return c[0] >= self.p1[0] and c[0] <= self.p2[0] and c[1] >= self.p1[1] and c[1] <= self.p2[1]

    def get_closest_edge(self, c):
        if c[1] > self.p1[1] and c[1] < self.p2[1]:
            if abs(c[0] - self.p1[0]) < SELECT_EDGE_DISTANCE:
                return self.p1, self.p3
            elif abs(c[0] - self.p2[0]) < SELECT_EDGE_DISTANCE:
                return self.p4, self.p2

        if c[0] > self.p1[0] and c[0] < self.p2[0]:
            if abs(c[1] - self.p1[1]) < SELECT_EDGE_DISTANCE:
                return self.p1, self.p4
            elif abs(c[1] - self.p2[1]) < SELECT_EDGE_DISTANCE:
                return self.p3, self.p2

    def set_coords(self, coords):
        self.p1 = (min(coords[0], coords[2]), min(coords[1], coords[3]))
        self.p2 = (max(coords[0], coords[2]), max(coords[1], coords[3]))
        self.p3 = (min(coords[0], coords[2]), max(coords[1], coords[3]))
        self.p4 = (max(coords[0], coords[2]), min(coords[1], coords[3]))

    def highlight_edge(self, edge):
        self.highlighted_edge = edge

    def draw(self, frame):
        cv2.rectangle(frame, self.p1, self.p2, (255, 0, 0))

        if self.highlighted_edge:
            cv2.line(frame, self.highlighted_edge[0], self.highlighted_edge[1], (255, 0, 0), thickness=3)

    def update_marker_corner(corneriasas, values):
        for i,c in enumerate(corneriasas):
            self.corners[c] = values[i]

class DefaultMode:
    def on_mousemove(self, c):
        State.mouse = c
        State.draw_frame()

        for marker in State.markers:
            edge = marker.get_closest_edge(c)
            marker.highlight_edge(edge)

    def on_lbuttondown(self, c, flags):
        # Ctrl + mousedown
        if flags & cv2.EVENT_FLAG_CTRLKEY:
            for marker in State.markers:
                if marker.contains_coord(c):
                    State.markers.remove(marker)
                    State.draw_frame()
                    break
            return

        # Mousedown
        highlighted_markers = list(filter(lambda marker: marker.highlighted_edge != None, State.markers))

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

        for marker in State.markers:
            marker.draw(frame)


class CreateMarkerMode(DefaultMode):
    def __init__(self, c):
        self.origin = c

    def on_lbuttondown(self, c, flags):
        State.markers.append(Marker(State.label, (*self.origin, *c)))
        State.draw_frame()
        State.mode = DefaultMode()

    def draw_frame(self, frame):
        super().draw_frame(frame)
        Marker(State.label, (*self.origin, *State.mouse)).draw(frame)


class ResizeMarkerMode(DefaultMode):
    def __init__(self, marker, edge):
        self.marker = marker
        self.edge = edge

        # Use y-axis if the x-coords of the edge coordinates are different, x-axis otherwise
        if edge[0][0] == edge[1][0]:
            self.axis = 0
        else:
            self.axis = 1

        self.fixed = list(filter(lambda p: not p in edge, (marker.p1, marker.p2, marker.p3, marker.p4)))

    def on_mousemove(self, c):
        print(*self.edge, c[self.axis])
        # 

    def on_lbuttonup(self, c):
        State.mode = DefaultMode()
        State.draw_frame()
    
    def draw_frame(self, frame):
        self.marker.draw(frame)


class State:
    image = None
    mouse = None
    markers = []
    label = 1
    mode = DefaultMode()

    @staticmethod
    def draw_frame():
        frame = State.image.copy()
        State.mode.draw_frame(frame)
        cv2.imshow(WINDOW_NAME, frame)

    @staticmethod
    def on_trackbar(value):
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
cv2.createTrackbar("", WINDOW_NAME, 0, FRAMES - 1, State.on_trackbar)
cv2.setMouseCallback(WINDOW_NAME, State.on_mouse)
State.on_trackbar(0)

# Event loop
while True:
    key = cv2.waitKey(10)

    if key == ord("q"):
        break

import os
import cv2
import argparse
import configparser
import sqlite3


# Get program arguments
parser = argparse.ArgumentParser()
parser.add_argument("--input")
parser.add_argument("--output", default="output/")
parser.add_argument("--resize", default="1280x720")
parser.add_argument("--tracker", default="dasiamrpn")
args = parser.parse_args()


# Constants
WINDOW_NAME = "Video annotation tool"
FRAME_TRACKBAR_NAME = "Frame"
INPUT_FILE_NAME = os.path.split(args.input)[1]
ABOUT_PATH = os.path.join(args.output, INPUT_FILE_NAME, "about.ini")
FRAMES_PATH = os.path.join(args.output, INPUT_FILE_NAME, "frames")
DB_PATH = os.path.join(args.output, INPUT_FILE_NAME, "markers.db")
IMAGE_SIZE = tuple([int(size) for size in args.resize.split("x")])
TRACKER_NAME = args.tracker
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

# Open database
db = sqlite3.connect(DB_PATH)
db_cur = db.cursor()

db_cur.execute("DROP TABLE rect_markers")
db_cur.execute("CREATE TABLE IF NOT EXISTS rect_markers (id INTEGER PRIMARY KEY, frame INTEGER, label INTEGER, x_min INTEGER, y_min INTEGER, x_max INTEGER, y_max INTEGER)")

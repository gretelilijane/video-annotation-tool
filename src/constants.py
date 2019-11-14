import os
import cv2
import argparse
import configparser
import sqlite3

# Get program arguments
parser = argparse.ArgumentParser()
parser.add_argument("--input", default="NO_INPUT")
parser.add_argument("--output", default="output.db")
parser.add_argument("--resize", default="640x360")
parser.add_argument("--tracker", default="dasiamrpn")
parser.add_argument("--labels", default="object")
args = parser.parse_args()


# Constants
WINDOW_NAME = "Video annotation tool"
FRAME_TRACKBAR_NAME = "Frame"
INPUT_FILE_NAME = os.path.split(args.input)[1]
DB_PATH = args.output
TRACKER_NAME = args.tracker
TRACKER_FRAME_SKIP = 10
SELECT_EDGE_DISTANCE = 10
LABELS = args.labels.split(",")
LABEL_DISPLAY_HEIGHT = 30
COLORS = (
    (164, 0, 0),
    (0, 164, 0),
    (0, 0, 164)
)

# Open database
db = sqlite3.connect(DB_PATH)
db_cur = db.cursor()

#db_cur.execute("DROP TABLE assets")
db_cur.execute("CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY, name TEXT, frame_count INTEGER, width INTEGER, height INTEGER)")
#db_cur.execute("DROP TABLE images")
db_cur.execute("CREATE TABLE IF NOT EXISTS images (asset_id INTEGER, frame INTEGER, data BLOB)")

# Prepare asset
if INPUT_FILE_NAME == "NO_INPUT":
    ASSET_ID = 0
else:
    db_cur.execute("SELECT id, frame_count, width, height FROM assets WHERE name = ? LIMIT 1", (INPUT_FILE_NAME, ))
    row = db_cur.fetchone()

    if row is not None:
        ASSET_ID = row[0]
        FRAME_COUNT = row[1]
        IMAGE_SIZE = (row[2], row[3])
    else:
        video = cv2.VideoCapture(args.input)
        FRAME_COUNT = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        IMAGE_SIZE = tuple([int(size) for size in args.resize.split("x")])

        db_cur.execute("INSERT INTO assets (name, frame_count, width, height) VALUES (?, ?, ?, ?)", (
            INPUT_FILE_NAME, FRAME_COUNT, *IMAGE_SIZE
        ))

        ASSET_ID = db_cur.lastrowid

        # Extract and resize all frames
        images = []

        for frame in range(FRAME_COUNT):
            _, image = video.read()
            _, blob = cv2.imencode(".jpg", cv2.resize(image, IMAGE_SIZE))

            images.append((ASSET_ID, frame, blob))
            print(frame)

        db_cur.executemany("INSERT INTO images (asset_id, frame, data) VALUES (?, ?, ?)", images)
        db.commit()

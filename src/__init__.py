import os
import cv2
import argparse
import click

from src import db

# Get program arguments
parser = argparse.ArgumentParser()
parser.add_argument("--input", default="NO_INPUT")
parser.add_argument("--output", default="output")
parser.add_argument("--resize", default="640x480")
parser.add_argument("--tracker", default="csrt")
parser.add_argument("--labels", default="NO_LABEL")
args = parser.parse_args()


# Constants
WINDOW_NAME = "Video annotation tool"
FRAME_TRACKBAR_NAME = "Frame"
INPUT_FILE_PATH = args.input
INPUT_FILE_NAME = os.path.split(args.input)[1]
OUTPUT_DIRECTORY = args.output
DB_PATH = os.path.join(OUTPUT_DIRECTORY, "sqlite.db")
TRACKER_NAME = args.tracker
TRACKER_FRAME_SKIP = 10
SELECT_EDGE_DISTANCE = 10
USED_LABELS = filter(lambda label: label != "NO_LABEL", args.labels.split(","))
LABEL_DISPLAY_HEIGHT = 30
COLORS = (
    (164, 0, 0),
    (0, 164, 0),
    (0, 0, 164)
)

try:
    os.makedirs(OUTPUT_DIRECTORY)
except FileExistsError:
    pass


# Open database
db.connect(DB_PATH)

#db.execute("DROP TABLE labels")
db.execute("CREATE TABLE IF NOT EXISTS labels (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)")
#db.execute("DROP TABLE assets")
db.execute("CREATE TABLE IF NOT EXISTS assets (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, frame_count INTEGER, width INTEGER, height INTEGER)")
#db.execute("DROP TABLE images")
db.execute("CREATE TABLE IF NOT EXISTS images (asset_id INTEGER, frame INTEGER, data BLOB)")

db.commit()


# Prepare labels
for label_name in USED_LABELS:
    try:
        db.execute("INSERT INTO labels (name) VALUES (?)", (label_name,))
        db.commit()
    except Exception:
        pass

db.execute("SELECT id, name FROM labels")
LABELS = db.fetchall()


# Prepare asset
if INPUT_FILE_NAME == "NO_INPUT":
    ASSET_ID = 0
else:
    db.execute("SELECT id, frame_count, width, height FROM assets WHERE name = ?", (INPUT_FILE_NAME, ))
    row = db.fetchone()

    if row is not None:
        ASSET_ID = row[0]
        FRAME_COUNT = row[1]
        IMAGE_SIZE = (row[2], row[3])
    else:
        IMAGE_SIZE = tuple([int(size) for size in args.resize.split("x")])
        images = []

        if os.path.isdir(INPUT_FILE_PATH):
            files = []

            for (dirpath, dirnames, filenames) in os.walk(INPUT_FILE_PATH):
                files += [os.path.join(dirpath, filename) for filename in filenames]

            FRAME_COUNT = len(files)

            with click.progressbar(range(FRAME_COUNT)) as frames:
                for frame in frames:
                    image = cv2.imread(files[frame])
                    crop_height = image.shape[1]*IMAGE_SIZE[1]//IMAGE_SIZE[0]
                    crop_offset = (image.shape[0] - crop_height) // 2

                    if crop_height < image.shape[0]:
                        image = image[crop_offset:(crop_offset+crop_height),:]

                    _, blob = cv2.imencode(".jpg", cv2.resize(image, IMAGE_SIZE))
                    images.append((frame, blob))
        else:
            video = cv2.VideoCapture(INPUT_FILE_PATH)
            FRAME_COUNT = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

            # Extract and resize all frames
            with click.progressbar(range(FRAME_COUNT)) as frames:
                for frame in frames:
                    _, image = video.read()
                    _, blob = cv2.imencode(".jpg", cv2.resize(image, IMAGE_SIZE))

                    images.append((frame, blob))

        db.execute("INSERT INTO assets (name, frame_count, width, height) VALUES (?, ?, ?, ?)", (
            INPUT_FILE_NAME, FRAME_COUNT, *IMAGE_SIZE
        ))

        ASSET_ID = db.lastrowid()

        db.executemany("INSERT INTO images (asset_id, frame, data) VALUES (%d, ?, ?)" % ASSET_ID, images)
        db.commit()

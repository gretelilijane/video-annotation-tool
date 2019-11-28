import os
import cv2
import numpy as np
import tensorflow as tf
import click
import re

from src import db, OUTPUT_DIRECTORY
from src.marker import marker_db


# Constants
PRETRAINED_MODELS_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "pretrained_models"))
PRETRAINED_MODEL_PATH = os.path.join(PRETRAINED_MODELS_PATH, "ssd_mobilenet_v1_quantized")
PRETRAINED_MODEL_CKPT = os.path.join(PRETRAINED_MODEL_PATH, "model.ckpt")
LABEL_MAP_PATH = os.path.join(OUTPUT_DIRECTORY, "label_map.pbtxt")
LABEL_TXT_PATH = os.path.join(OUTPUT_DIRECTORY, "labels.txt")
TEST_RECORD_PATH = os.path.join(OUTPUT_DIRECTORY, "test.record")
TRAIN_RECORD_PATH = os.path.join(OUTPUT_DIRECTORY, "train.record")


# Get labels
label_names = {}

db.execute("SELECT id, name FROM labels")

for row in db.fetchall():
    label_names[row[0]] = row[1]


# Generate TF records
test_writer = tf.io.TFRecordWriter(TEST_RECORD_PATH)
train_writer = tf.io.TFRecordWriter(TRAIN_RECORD_PATH)

db.execute("SELECT id, name, frame_count, width, height FROM assets")
assets = db.fetchall()
used_label_ids = []
test_set_size = 0

for asset in assets:
    asset_id, asset_name, frame_count, width, height = asset
    max_coords = np.array((width, height, width, height))
    print(asset_name)

    indices = np.array(range(frame_count))
    test_set = np.random.choice(indices, frame_count // 4, replace=False)

    with click.progressbar(range(frame_count)) as frames:
        for frame in frames:
            db.execute("SELECT data FROM images WHERE asset_id=? AND frame=?", (asset_id, frame))
            image_data = db.fetchone()[0]

            markers = marker_db.get_markers_by_clause("WHERE asset_id=? AND frame=?", (asset_id, frame))
            coords = [marker.get_coords() / max_coords for marker in markers]

            if len(markers) == 0:
                continue

            for marker in markers:
                if not marker.label_id in used_label_ids:
                    used_label_ids.append(marker.label_id)

            tf_example = tf.train.Example(features=tf.train.Features(feature={
                "image/width": tf.train.Feature(int64_list=tf.train.Int64List(value=[
                    width
                ])),
                "image/height": tf.train.Feature(int64_list=tf.train.Int64List(value=[
                    height
                ])),
                "image/filename": tf.train.Feature(bytes_list=tf.train.BytesList(value=[
                    asset_name.encode("utf8")
                ])),
                "image/source_id": tf.train.Feature(bytes_list=tf.train.BytesList(value=[
                    (asset_name + "-" + str(frame)).encode("utf8")
                ])),
                "image/encoded": tf.train.Feature(bytes_list=tf.train.BytesList(value=[
                    image_data
                ])),
                "image/format": tf.train.Feature(bytes_list=tf.train.BytesList(value=[
                    b"jpg"
                ])),
                "image/object/bbox/xmin": tf.train.Feature(float_list=tf.train.FloatList(value=[
                    coord[0] for coord in coords
                ])),
                "image/object/bbox/ymin": tf.train.Feature(float_list=tf.train.FloatList(value=[
                    coord[1] for coord in coords
                ])),
                "image/object/bbox/xmax": tf.train.Feature(float_list=tf.train.FloatList(value=[
                    coord[2] for coord in coords
                ])),
                "image/object/bbox/ymax": tf.train.Feature(float_list=tf.train.FloatList(value=[
                    coord[3] for coord in coords
                ])),
                "image/object/class/text": tf.train.Feature(bytes_list=tf.train.BytesList(value=[
                    label_names[marker.label_id].encode("utf8") for marker in markers
                ])),
                "image/object/class/label": tf.train.Feature(int64_list=tf.train.Int64List(value=[
                    (used_label_ids.index(marker.label_id) + 1) for marker in markers
                ]))
            }))

            if frame in test_set:
                test_set_size += 1
                test_writer.write(tf_example.SerializeToString())
            else:
                train_writer.write(tf_example.SerializeToString())

test_writer.close()
train_writer.close()


# Generate pipeline config
replacements = {
    "NUM_CLASSES": str(len(used_label_ids)),
    "FINE_TUNE_CHECKPOINT": PRETRAINED_MODEL_CKPT.replace("\\", "\\\\"),
    "LABEL_MAP_PATH": LABEL_MAP_PATH.replace("\\", "\\\\"),
    "TRAIN_RECORD_PATH": TRAIN_RECORD_PATH.replace("\\", "\\\\"),
    "TEST_RECORD_PATH": TEST_RECORD_PATH.replace("\\", "\\\\"),
    "NUM_EXAMPLES": str(test_set_size)
}

with open(os.path.join(OUTPUT_DIRECTORY, "pipeline.config"), "w") as pipeline:
    with open(os.path.join(PRETRAINED_MODEL_PATH, "pipeline.config")) as base_pipeline:
        content = base_pipeline.read()

        for key, value in replacements.items():
            content = content.replace("${%s}" % key, value)
        
        pipeline.write(content)


# Generate label maps
with open(LABEL_MAP_PATH, "w") as label_map:
    label_map.write("item {\n    id: 0\n    name: 'background'\n}\n\n")

    for index, label_id in enumerate(used_label_ids):
        label_map.write("item {\n    id: %d\n    name: '%s'\n}\n\n" % (index + 1, label_names[label_id]))

with open(LABEL_TXT_PATH, "w") as label_txt:
    label_txt.write("0 background")

    for index, label_id in enumerate(used_label_ids):
        label_txt.write("\n%d %s" % (index + 1, label_names[label_id]))

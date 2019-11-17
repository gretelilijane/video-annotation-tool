import cv2
import numpy as np
import tensorflow as tf

from src import db
from src.marker import marker_db

#test_writer = tf.python_io.TFRecordWriter(os.path.join(AssetTree.project_path, "config", "test.record"))
#train_writer = tf.python_io.TFRecordWriter(os.path.join(AssetTree.project_path, "config", "train.record"))

db.execute("SELECT id, frame_count, width, height FROM assets")
assets = db.fetchall()

for asset in assets:
    asset_id, frame_count, width, height = asset
    
    for frame in range(frame_count):
        db.execute("SELECT data FROM images WHERE asset_id=? AND frame=?", (asset_id, frame))
        data = db.fetchone()[0]

        markers = marker_db.get_markers_by_clause("WHERE asset_id=? AND frame=?", (asset_id, frame))
        for marker in markers:
            print(marker.label_id, marker.get_coords())
        break



'''
for asset_path in iterate_assets(AssetTree.path):
    with open(asset_path + ".markers.csv", "r") as file:
        reader = csv.reader(file)

        # Read markers
        markers = dict()
        total = 0

        for row in reader:
            _, frame_id, _marker_id, label_id, x0, y0, x1, y1 = row

            if not frame_id in markers:
                total += 1
                markers[frame_id] = []

            markers[frame_id].append({
                "label_id": label_id,
                "coords": [float(c) for c in (x0, y0, x1, y1)]
            })

        # Generate training and test sets
        indices = np.array(range(total))
        test_set = np.random.choice(indices, total // 10, replace=False)

        # Get frames
        video = Video(asset_path)
        index = 0

        for frame in range(video.frame_count):
            frame_id = str(frame)

            if not frame_id in markers:
                continue

            resized = cv2.resize(video.image, (400, 225))
            encoded = cv2.imencode(".jpg", resized)[1].tostring()

            tf_example = tf.train.Example(features=tf.train.Features(feature={
                "image/width": tf.train.Feature(int64_list=tf.train.Int64List(value=[400])),
                "image/height": tf.train.Feature(int64_list=tf.train.Int64List(value=[225])),
                "image/filename": tf.train.Feature(bytes_list=tf.train.BytesList(value=[
                    os.path.basename(asset_path).encode("utf8")
                ])),
                "image/source_id": tf.train.Feature(bytes_list=tf.train.BytesList(value=[
                    os.path.basename(asset_path).encode("utf8")
                ])),
                "image/encoded": tf.train.Feature(bytes_list=tf.train.BytesList(value=[encoded])),
                "image/format": tf.train.Feature(bytes_list=tf.train.BytesList(value=[b"jpg"])),
                "image/object/bbox/xmin": tf.train.Feature(float_list=tf.train.FloatList(value=[
                    marker["coords"][0] for marker in markers[frame_id]
                ])),
                "image/object/bbox/ymin": tf.train.Feature(float_list=tf.train.FloatList(value=[
                    marker["coords"][1] for marker in markers[frame_id]
                ])),
                "image/object/bbox/xmax": tf.train.Feature(float_list=tf.train.FloatList(value=[
                    marker["coords"][2] for marker in markers[frame_id]
                ])),
                "image/object/bbox/ymax": tf.train.Feature(float_list=tf.train.FloatList(value=[
                    marker["coords"][3] for marker in markers[frame_id]
                ])),
                "image/object/class/text": tf.train.Feature(bytes_list=tf.train.BytesList(value=[
                    "toy".encode("utf8") for marker in markers[frame_id]
                ])),
                "image/object/class/label": tf.train.Feature(int64_list=tf.train.Int64List(value=[
                    1 for marker in markers[frame_id]
                ]))
            }))

            if index in test_set:
                test_writer.write(tf_example.SerializeToString())
            else:
                train_writer.write(tf_example.SerializeToString())

            video.forward()
            index += 1
            print(index)

    print("export", asset_path)

test_writer.close()
train_writer.close()
'''

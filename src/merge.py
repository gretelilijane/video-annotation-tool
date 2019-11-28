import cv2
import os
import numpy as np
import sqlite3

from src import db
from src import args, LABELS
from src.marker import marker_db

conn = sqlite3.connect(args.source)
cur = conn.cursor()

# Merge labels
merge_labels_map = {}
cur.execute("SELECT id, name FROM labels")

for label in cur.fetchall():
    is_new = True

    for current_label in LABELS:
        if label[1] == current_label[1]:
            is_new = False
            merge_labels_map[label[0]] = current_label[0]
            break
    
    if is_new:
        db.execute("INSERT INTO labels (name) VALUES (?)", (label[1], ))
        merge_labels_map[label[0]] = db.lastrowid()

print("label map:", merge_labels_map)

# Merge assets
db.execute("SELECT id, name FROM assets")
assets = db.fetchall()

merge_assets_map = {}
cur.execute("SELECT id, name, frame_count, width, height FROM assets")

for asset in cur.fetchall():
    is_new = True

    for current_asset in assets:
        if asset[1] == current_asset[1]:
            is_new = False
            merge_assets_map[asset[0]] = current_asset[0]
            break

    if is_new:
        db.execute("INSERT INTO assets (name, frame_count, width, height) VALUES (?, ?, ?, ?)", asset[1:])
        merge_assets_map[asset[0]] = db.lastrowid()

        # Merge images
        cur.execute("SELECT frame, data FROM images WHERE asset_id = ?", (asset[0], ))
        images = cur.fetchall()
        db.executemany("INSERT INTO images (asset_id, frame, data) VALUES (%d, ?, ?)" % merge_assets_map[asset[0]], images)

print("asset map:", merge_assets_map)

# Merge rect markers
cur.execute("SELECT id, asset_id, frame, label_id, trackable, x_min, y_min, x_max, y_max FROM rect_markers")

for marker in cur.fetchall():
    db.execute("INSERT INTO rect_markers (asset_id, frame, label_id, trackable, x_min, y_min, x_max, y_max) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
        merge_assets_map[marker[1]],
        marker[2],
        merge_labels_map[marker[3]],
        *marker[4:]
    ))

# TODO: merge interpolated markers

# Done
conn.close()

db.commit()
db.close()

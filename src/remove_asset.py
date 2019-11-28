import cv2
import os
import numpy as np

from src import db
from src.mode.default_mode import DefaultMode
from src.mode.create_marker_mode import CreateMarkerMode
from src.mode.resize_marker_mode import ResizeMarkerMode
from src.mode.track_mode import TrackMode
from src.marker.marker_db import delete_markers_by_clause
from src import *

db.execute("DELETE FROM assets WHERE id=?", (ASSET_ID, ))
db.execute("DELETE FROM images WHERE asset_id=?", (ASSET_ID, ))
delete_markers_by_clause("WHERE asset_id=?", (ASSET_ID, ))
db.commit()

db.close()

import os
import cv2
import numpy as np
import tensorflow as tf
from math import isnan

from src import WINDOW_NAME, OUTPUT_DIRECTORY, ASSET_ID, FRAME_COUNT, db

# Constants
MODEL_PATH = os.path.join(OUTPUT_DIRECTORY, "detect.tflite")

# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Play video
cv2.namedWindow(WINDOW_NAME)

for frame in range(FRAME_COUNT):
    db.execute("SELECT data FROM images WHERE asset_id=? AND frame=?", (ASSET_ID, frame))
    row = db.fetchone()
    image = cv2.imdecode(np.frombuffer(row[0], np.uint8), cv2.IMREAD_UNCHANGED)

    image_input = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_input = cv2.resize(image, (300, 300))
    image_input = image_input.reshape(1, *image_input.shape)
    image_input = image_input.astype(np.uint8)
    
    interpreter.set_tensor(input_details[0]["index"], image_input)
    interpreter.invoke()

    boxes = interpreter.get_tensor(output_details[0]["index"])
    labels = interpreter.get_tensor(output_details[1]["index"])
    scores = interpreter.get_tensor(output_details[2]["index"])
    num = interpreter.get_tensor(output_details[3]["index"])

    for i in range(boxes.shape[1]):
        if scores[0, i] < 0.25:
            continue

        box = boxes[0, i, :]

        if isnan(box[0]) or isnan(box[1]) or isnan(box[2]) or isnan(box[3]) or box[0] < 0 or box[1] < 0 or box[2] > 1 or box[3] > 1:
            continue

        x0 = int(box[1] * image.shape[1])
        y0 = int(box[0] * image.shape[0])
        x1 = int(box[3] * image.shape[1])
        y1 = int(box[2] * image.shape[0])

        cv2.rectangle(image, (x0, y0), (x1, y1), (255, 0, 0), 2)
        cv2.rectangle(image, (x0, y0), (x0 + 100, y0 - 30), (255, 0, 0), -1)
        cv2.putText(image,
                str(int(labels[0, i])), (x0, y0),
                cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 255, 255), 2)

    cv2.imshow(WINDOW_NAME, image)

    if cv2.waitKey(15) == ord("q"):
        break

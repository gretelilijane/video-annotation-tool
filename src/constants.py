import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input")
parser.add_argument("--output", default="output/")
parser.add_argument("--resize", default="1280x720")
parser.add_argument("--tracker", default="dasiamrpn")
args = parser.parse_args()

WINDOW_NAME = "Video annotation tool"
INPUT_FILE_NAME = os.path.split(args.input)[1]
ABOUT_PATH = os.path.join(args.output, INPUT_FILE_NAME, "about.ini")
FRAMES_PATH = os.path.join(args.output, INPUT_FILE_NAME, "frames")
IMAGE_SIZE = tuple([int(size) for size in args.resize.split("x")])
TRACKER_NAME = args.tracker
SELECT_EDGE_DISTANCE = 10

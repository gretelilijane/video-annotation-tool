# Ensure DaSiamRPN code is available
import sys
from os.path import join, dirname, exists

DaSiamRPN_path = join(dirname(__file__), "..", "..", "lib", "DaSiamRPN", "code")

if not exists(DaSiamRPN_path):
    print("DaSiamRPN has not been downloaded. Please run `git submodule update --init --recursive` to fix this.")
    exit()

sys.path.append(DaSiamRPN_path)

# Create DaSiamRPN bridge
import torch
import numpy as np

from lib.DaSiamRPN.code.run_SiamRPN import SiamRPN_init, SiamRPN_track
from lib.DaSiamRPN.code.utils import get_axis_aligned_bbox, cxy_wh_2_rect
from lib.DaSiamRPN.code.net import SiamRPNvot


DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
MODEL_PATH = join(dirname(__file__), "..", "..", "pretrained_models", "SiamRPNVOT.model")


class DaSiamRPNTracker:
    def __init__(self):
        self.net = SiamRPNvot()
        self.net.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        self.net.eval().to(DEVICE)

    def init(self, image, coords):
        center = np.array((
            (coords[0] + coords[2]) / 2,
            (coords[1] + coords[3]) / 2
        ), dtype=int)

        size = np.array((
            coords[2] - coords[0],
            coords[3] - coords[1]
        ), dtype=int)

        self.tracker_state = SiamRPN_init(image, center, size, self.net, DEVICE)

    def update(self, image):
        self.tracker_state = SiamRPN_track(self.tracker_state, image, DEVICE)
        center, size = self.tracker_state["target_pos"], self.tracker_state["target_sz"]

        return (
            int(center[0] - size[0]/2),
            int(center[1] - size[1]/2),
            int(center[0] + size[0]/2),
            int(center[1] + size[1]/2)
        )

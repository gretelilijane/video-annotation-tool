## Installation

Run `pip install -r requirements.txt` to install pip dependencies and `git submodule update --init --recursive` to download the required submodules.

## Running

Run `python -m src.main --input path_to_mp4_file [--output path_to_output_dir] [--resize 1280x720] [--tracker dasiamrpn]`. The default output
directory is `output/`, the default resized image size is `1280x720` and the default tracker is `dasiamrpn`.

## Usage

* Left mouse down: start creating new marker
* Left mouse down: stop creating new marker
* Ctrl + Left mouse button: remove marker

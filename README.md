## Installation

Run `pip install -r requirements.txt` to install pip dependencies and `git submodule update --init --recursive` to download the required submodules.

## Running

Run `python -m src.main --input path_to_mp4_file --labels object1,object2 [--output path_to_output_dir] [--resize 640x480] [--tracker csrt | dasiamrpn]`. The default output
directory is `output/`, the default resized image size is `640x480` and the default tracker is `csrt`.

## Usage

* Click and drag: create marker
* Ctrl + Left mouse button: remove marker

## Training

```
python3 -m object_detection.model_main --logtostderr --train_dir=output/ --pipeline_config_path=output/pipeline.config --model_dir=output/model/ --input_type image_tensor --input_shape 1,300,300,3
```

## TFLite

Generate frozen graph with TensorFlow Lite compatible ops:
```
python3 -m object_detection.export_tflite_ssd_graph --pipeline_config_path=output/pipeline.config --trained_checkpoint_prefix=output/model/model.ckpt-2412 --output_directory=output/graph --add_postprocessing_op=true
```

Convert frozen graph to TensorFlow Lite optimized model:
```
tflite_convert --graph_def_file=output/graph/tflite_graph.pb --output_file=output/detect.tflite --input_shapes=1,300,300,3 --input_arrays=normalized_input_image_tensor --output_arrays=TFLite_Detection_PostProcess,TFLite_Detection_PostProcess:1,TFLite_Detection_PostProcess:2,TFLite_Detection_PostProcess:3 --inference_type=QUANTIZED_UINT8 --mean_values=128 --std_dev_values=128 --change_concat_input_ranges=false --allow_nudging_weights_to_use_fast_gemm_kernel=true --allow_custom_ops
```

## Compiling for Edge TPU

Compile model for edgetpu:
```
edgetpu_compiler -s -m 10 -o output output/detect.tflite
```

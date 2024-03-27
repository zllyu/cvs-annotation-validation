# Video Trimming Script

## Description
This Python script automates the process of trimming `.mp4` videos to a specific frame count (2700 frames, approximately 90 seconds, assuming 30 FPS). It can process a single video or batch process an entire directory of videos. The script also skips over any files that are not in `.mp4` format and provides feedback on the processing steps.

## Requirements
- Python 3.x
- OpenCV (opencv-python==4.9.0.80)
- argparse (built-in module)

Refer to requirements.txt for the complete list of dependencies.

## Setup
1. Ensure Python 3.x is installed on your system.
2. Install the required packages using pip:
    ```
    pip install -r requirements.txt
    ```
3. Place `trim_videos.py` in your project directory.

## Usage
```
python trim_videos.py --source_path PATH_TO_VIDEO_OR_DIRECTORY --new_video_dir PATH_TO_SAVE_TRIMMED_VIDEOS
```
- `--source_path`: The path to a single video file or a directory containing multiple `.mp4` videos.
- `--new_video_dir`: The directory where the trimmed videos will be saved.

***
# Annotation Processing Script

## Description
This script processes annotations from a JSON file, organizing the data into Excel sheets for both frame-level and video-level annotations. It also generates an Excel sheet for annotations that are incomplete. This tool is particularly useful for managing and analyzing video annotation projects.

## Requirements
- Python 3.x
- pandas (`pandas==1.5.2`)
- openpyxl (`openpyxl==3.1.2`)
- numpy (`numpy==1.23.5`)
- argparse (built-in module)

Refer to `requirements.txt` for the complete list of dependencies.

## Setup
1. Ensure Python 3.x is installed on your system.
2. Install the required packages using pip:
    ```
    pip install -r requirements.txt
    ```
3. Place `annotation_completion_test.py` in your project directory.

## Usage
```
python annotation_completion_test.py --input_file PATH_TO_INPUT_JSON --output_frame PATH_TO_FRAME_OUTPUT_XLSX --output_video PATH_TO_VIDEO_OUTPUT_XLSX --output_incomplete PATH_TO_INCOMPLETE_OUTPUT_XLSX
```
- `--input_file`: The path to the JSON file containing the annotations.
- `--output_frame`: The path where the frame level annotations Excel file will be saved.
- `--output_video`: The path where the video level annotations Excel file will be saved.
- `--output_incomplete`: The path where the Excel file for incomplete annotations will be saved.
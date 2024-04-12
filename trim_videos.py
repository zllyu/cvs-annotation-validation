import cv2
import os
import argparse
from datetime import datetime


SUCCESS_LOG = "success_videos.txt"
FAIL_LOG = "error_videos.txt"
PROCESSING_LOG = "video_processing.log"


def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(PROCESSING_LOG, 'a') as log_file:
        log_file.write(f"{timestamp} - {message}\n")


def get_video_info(cap):
    if not cap.isOpened():
        return None, None, None  # Indicates the video couldn't be opened
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fps == 0:  # Prevent division by zero
        return None, None, None  # Indicates an error in reading FPS
    video_duration = total_frames / fps
    return fps, total_frames, video_duration


def trim_video(cap, fps, output_path):
    # get the video's information
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # set up outputs
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # encoder for .mp4 file
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # trim the video to exact 2700 frames (90 seconds)
    count = 0  # Number of frames processed
    while True:
        ret, frame = cap.read()
        if not ret or count >= 2700:
            break
        out.write(frame)
        count += 1

    # release resource
    out.release()


def read_processed_videos():
    if os.path.exists(SUCCESS_LOG):
        with open(SUCCESS_LOG, 'r') as file:
            return set(file.read().splitlines())
    return set()


def process_video(video_path, new_video_dir, processed_videos):
    video_name = os.path.basename(video_path)
    if video_name in processed_videos:
        log_message(f"Skipping {video_name}: already processed")
        return

    if not video_name.lower().endswith('.mp4'):
        log_message(f"Skipping {video_name}: not an .mp4 file")
        return
    
    # Define paths for trimmed and untrimmed subdirectories
    trimmed_path = os.path.join(new_video_dir, "success", "trimmed")
    untrimmed_path = os.path.join(new_video_dir, "success", "untrimmed")

    # Create the subdirectories if they do not exist
    os.makedirs(trimmed_path, exist_ok=True)
    os.makedirs(untrimmed_path, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    fps, total_frames, _ = get_video_info(cap)

    if fps is None or total_frames is None:
        output_path = os.path.join(new_video_dir, "fail", video_name)
        log_message(f"Failed to process {video_name}: unable to read video information or corrupted file.")
        if not os.path.exists(output_path):
            os.rename(video_path, output_path)  # Move corrupted or unreadable files to 'fail' directory
        cap.release()
        with open(FAIL_LOG, 'a') as file:
            file.write(f"{video_name}\n")
        return

    if total_frames == 2700:
        output_path = os.path.join(untrimmed_path, video_name)
        os.rename(video_path, output_path)
        log_message(f"Video {video_name} is correct length, no trim needed.")
        with open(SUCCESS_LOG, 'a') as file:
            file.write(f"{video_name}\n")
    elif total_frames > 2700:
        output_path = os.path.join(trimmed_path, video_name)
        trim_video(cap, fps, output_path)
        log_message(f"Trimmed {video_name} to 2700 frames. Original frames: {total_frames}.")
        with open(SUCCESS_LOG, 'a') as file:
            file.write(f"{video_name}\n")
    else:
        output_path = os.path.join(new_video_dir, "fail", video_name)
        os.rename(video_path, output_path)
        log_message(f"Video {video_name} has less than 2700 frames, marked as error. Original frames: {total_frames}.")
        with open(FAIL_LOG, 'a') as file:
            file.write(f"{video_name}\n")

    cap.release()


def main(source_path, new_video_dir):
    success_dir = os.path.join(new_video_dir, "success")
    fail_dir = os.path.join(new_video_dir, "fail")
    os.makedirs(success_dir, exist_ok=True)
    os.makedirs(fail_dir, exist_ok=True)

    processed_videos = read_processed_videos()

    if os.path.isdir(source_path):
        for video_name in os.listdir(source_path):
            video_path = os.path.join(source_path, video_name)
            process_video(video_path, new_video_dir, processed_videos)
    elif os.path.isfile(source_path) and source_path.lower().endswith('.mp4'):
        process_video(source_path, new_video_dir, processed_videos)
    else:
        log_message("The specified source path does not exist or is not an .mp4 file.")
    
    log_message("... LOG END ...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Batch trim .mp4 videos.')
    parser.add_argument('--source_path', type=str, required=True, help='Path to the source video file or directory containing video files.')
    parser.add_argument('--new_video_dir', type=str, required=True, help='Directory path to save trimmed videos.')

    args = parser.parse_args()
    
    main(args.source_path, args.new_video_dir)
import cv2
import os
import argparse


def get_video_info(cap):
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
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


def process_video(video_path, new_video_dir):
    video_name = os.path.basename(video_path)
    if not video_name.lower().endswith('.mp4'):
        print(f"Skipping {video_name}: not an .mp4 file")
        return
    
    new_video_path = os.path.join(new_video_dir, video_name)

    # get the original video's information
    cap_old = cv2.VideoCapture(video_path)
    fps_old, total_frames_old, video_duration_old = get_video_info(cap_old)

    # decide whether the video needs to be trimmed
    if total_frames_old <= 2700:
        print(f"Video {video_name} doesn't need to be trimmed.")
        cap_old.release()
        return
    
    print(f"### Before\n {video_name} Duration: {video_duration_old} seconds, Total Frames: {total_frames_old}")
    
    # trim the video to exact 90 seconds
    trim_video(cap_old, fps_old, new_video_path)

    # print out trimmed video's information
    cap_new = cv2.VideoCapture(new_video_path)
    _, total_frames_new, video_duration_new = get_video_info(cap_new)
    print(f"### After\n {video_name} Duration: {video_duration_new} seconds, Total Frames: {total_frames_new}")

    # release resources
    cap_old.release()
    cap_new.release()


def main(source_path, new_video_dir):
    if not os.path.exists(new_video_dir):
        os.makedirs(new_video_dir)

    if os.path.isdir(source_path):
        # batch
        for video_name in os.listdir(source_path):
            video_path = os.path.join(source_path, video_name)
            if os.path.isfile(video_path) and video_path.lower().endswith('.mp4'):
                process_video(video_path, new_video_dir)
    elif os.path.isfile(source_path) and source_path.lower().endswith('.mp4'):
        # single video
        process_video(source_path, new_video_dir)
    else:
        print("The specified source path does not exist or is not an .mp4 file.")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Batch trim .mp4 videos.')
    parser.add_argument('--source_path', type=str, required=True, help='Path to the source video file or directory containing video files.')
    parser.add_argument('--new_video_dir', type=str, required=True, help='Directory path to save trimmed videos.')

    args = parser.parse_args()
    
    main(args.source_path, args.new_video_dir)
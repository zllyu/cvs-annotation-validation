import pandas as pd
import json
import numpy as np
import argparse


def process_annotations(input_file, output_frame, output_video, output_incomplete):
# Load the JSON data from the file
    with open(input_file) as file:  # Replace with your actual file path
        data = json.load(file)

    # Initialize empty lists for the two categories of data
    cvs_frame_data = []
    cvs_video_data = []

    # Iterate through each video and its annotations
    for video in data:
        video_id = video['videoId']
        
        # For CVS Video and CVS Video Difficulty, we'll need to combine data, so we prepare a dict
        video_difficulty_mapping = {}

        for annotation in video['annotations']:
            label_name = annotation['label']['name']
            node_id = annotation['nodeId']
            
            # Handling "CVS Frame" annotations
            if label_name == "CVS Frame":
                frame_row = {
                    'videoId': video_id,
                    'nodeId': node_id,  # Renamed nodeId for clarity
                    'rater1': None, 'rater2': None, 'rater3': None, 
                    # Initialize placeholders for rater information
                    'c1_rater1': None, 'c1_rater2': None, 'c1_rater3': None,
                    'c2_rater1': None, 'c2_rater2': None, 'c2_rater3': None,
                    'c3_rater1': None, 'c3_rater2': None, 'c3_rater3': None
                }
                # Extract ratings for each rater
                for feature in annotation['formFeatures']:
                    name = feature['name']
                    answers = feature['answers']
                    category = None
                    
                    if name == "2 Structures":
                        category = 'c1'
                    elif name == "Hepatocystic Triangle":
                        category = 'c2'
                    elif name == "Cystic Plate":
                        category = 'c3'
                    
                    if category:
                        for i, answer in enumerate(answers):
                            if i < 3:  # Only consider the first three raters
                                frame_row[f'{category}_rater{i+1}'] = answer['value']
                                frame_row[f'rater{i+1}'] = answer['userName']  # Assign rater names
                cvs_frame_data.append(frame_row)
            
            # Handling "CVS Video" and "CVS Video Difficulty" annotations
            elif label_name in ["CVS Video", "CVS Video Difficulty"]:
                # We use videoId and nodeId as keys to align difficulty ratings with the corresponding video
                key = (video_id, node_id)
                if key not in video_difficulty_mapping:
                    video_difficulty_mapping[key] = {
                        'videoId': video_id,
                        'video_nodeId': None,
                        'difficulty_nodeId': None,
                        'rater1': None, 'rater2': None, 'rater3': None,
                        'c1_rater1': None, 'c2_rater1': None, 'c3_rater1': None,
                        'c1_rater2': None, 'c2_rater2': None, 'c3_rater2': None,
                        'c1_rater3': None, 'c2_rater3': None, 'c3_rater3': None,
                        'difficulty_rater1': None, 'difficulty_rater2': None, 'difficulty_rater3': None
                    }
                
                # Populate the dictionary based on annotation type
                if label_name == "CVS Video":
                    video_difficulty_mapping[key]['video_nodeId'] = str(node_id)
                elif label_name == "CVS Video Difficulty":
                    video_difficulty_mapping[key]['difficulty_nodeId'] = str(node_id)

                for feature in annotation['formFeatures']:
                    for i, answer in enumerate(feature['answers']):
                        if i < 3:  # Only consider the first three raters
                            if label_name == "CVS Video Difficulty":
                                video_difficulty_mapping[key][f'difficulty_rater{i+1}'] = answer['value']
                            else:  # For CVS Video, handle classification and rater names
                                video_difficulty_mapping[key][f'rater{i+1}'] = answer['userName']
                                category = 'c1' if feature['name'] == "2 Structures" else 'c2' if feature['name'] == "Hepatocystic Triangle" else 'c3' if feature['name'] == "Cystic Plate" else None
                                if category:
                                    video_difficulty_mapping[key][f'{category}_rater{i+1}'] = answer['value']

                # Add the processed video and difficulty data to the list
                cvs_video_data.append(video_difficulty_mapping[key])

    df_cvs_frame = pd.DataFrame(cvs_frame_data)
    df_cvs_video = pd.DataFrame(cvs_video_data)
    df_cvs_video = df_cvs_video.groupby('videoId', as_index=False).first()

    # Find videoIds with None values in df_cvs_frame
    frame_none_video_ids = df_cvs_frame[df_cvs_frame.isnull().any(axis=1)]['videoId'].unique()
    # Find videoIds with None values in df_cvs_video
    video_none_video_ids = df_cvs_video[df_cvs_video.isnull().any(axis=1)]['videoId'].unique()
    # Combine and de-duplicate videoIds
    all_none_video_ids = pd.unique(np.concatenate((frame_none_video_ids, video_none_video_ids)))
    # Create a new DataFrame with the videoIds that contain None values
    df_video_ids_with_none = pd.DataFrame(all_none_video_ids, columns=['videoId'])

    df_cvs_frame.to_excel(output_frame, index=False)
    df_cvs_video.to_excel(output_video, index=False)
    df_video_ids_with_none.to_excel(output_incomplete, index=False)


def main():
     # Setup command-line argument parsing
    parser = argparse.ArgumentParser(description='Process CVS annotations.')
    parser.add_argument('--input_file', required=True, help='Path to the input JSON file containing annotations')
    parser.add_argument('--output_frame', required=True, help='Path to the output Excel file for frame level annotations')
    parser.add_argument('--output_video', required=True, help='Path to the output Excel file for video level annotations')
    parser.add_argument('--output_incomplete', required=True, help='Path to the output Excel file for incomplete annotations')
    args = parser.parse_args()
    
    # Call the process_annotations function with the parsed arguments
    process_annotations(args.input_file, args.output_frame, args.output_video, args.output_incomplete)


if __name__ == '__main__':
    main()
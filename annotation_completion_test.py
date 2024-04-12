import pandas as pd
import json
import numpy as np
import argparse
import os


def process_annotations(input_file):  # , output_frame, output_video, output_incomplete):
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

    # Merging df_cvs_frame and df_cvs_video on 'videoId'
    df_combined = pd.merge(df_cvs_frame, df_cvs_video, on='videoId', how='outer')

    # Handling videoId row counts and NaN values
    df_wrong = pd.DataFrame()
    for video_id in df_combined['videoId'].unique():
        video_rows = df_combined[df_combined['videoId'] == video_id]
        if len(video_rows) < 18 or video_rows.isnull().values.any():
            df_wrong = pd.concat([df_wrong, video_rows])
            df_combined = df_combined[df_combined['videoId'] != video_id]
            df_cvs_frame = df_cvs_frame[df_cvs_frame['videoId'] != video_id]
            df_cvs_video = df_cvs_video[df_cvs_video['videoId'] != video_id]
        elif len(video_rows) > 18:
            # If there are more than 18 rows for a videoId, keep only the first 18
            excess_rows_combined = video_rows.iloc[18:]
            df_wrong = pd.concat([df_wrong, excess_rows_combined])
            # Remove excess rows from df_combined
            df_combined = df_combined.drop(excess_rows_combined.index)

            excess_rows_indices_frame = df_cvs_frame[df_cvs_frame['videoId'] == video_id].index
            if len(excess_rows_indices_frame) > 18:
                df_cvs_frame = df_cvs_frame.drop(excess_rows_indices_frame[18:])

    # Adding video_name to DataFrames from the CSV mapping
    mapping_df = pd.read_csv('source_metadata/name_id_mapping_2024-04-03 22_02_23.634683.csv')
    mapping_df['videoId'] = mapping_df['videoId'].astype(str)

    # Merge each DataFrame with mapping_df to add the 'video_name' column
    df_cvs_frame['videoId'] = df_cvs_frame['videoId'].astype(str)
    df_cvs_frame = pd.merge(df_cvs_frame, mapping_df, on='videoId', how='left')
    df_cvs_video['videoId'] = df_cvs_video['videoId'].astype(str)
    df_cvs_video = pd.merge(df_cvs_video, mapping_df, on='videoId', how='left')
    df_combined['videoId'] = df_combined['videoId'].astype(str)
    df_combined = pd.merge(df_combined, mapping_df, on='videoId', how='left')
    df_wrong['videoId'] = df_wrong['videoId'].astype(str)
    df_wrong = pd.merge(df_wrong, mapping_df, on='videoId', how='left')

    # Output DataFrames to Excel
    df_cvs_frame.to_excel('annotation-outputs/output_frame.xlsx', index=False)
    df_cvs_video.to_excel('annotation-outputs/output_video.xlsx', index=False)
    df_combined.to_excel('annotation-outputs/output_combined.xlsx', index=False)
    df_wrong.to_excel('annotation-outputs/output_wrong.xlsx', index=False)

    # Assuming the directory where this script is running has write permission
    main_output_dir = 'external_outputs'
    os.makedirs(main_output_dir, exist_ok=True)

    # Step 1: Removing specified columns
    df_cvs_frame = df_cvs_frame.drop(columns=['videoId', 'nodeId', 'rater1', 'rater2', 'rater3'])
    df_cvs_video = df_cvs_video.drop(columns=['videoId', 'video_nodeId', 'difficulty_nodeId', 'rater1', 'rater2', 'rater3'])

    # Process each video_name for df_cvs_frame and df_cvs_video
    unique_video_names = pd.concat([df_cvs_frame['video_name'], df_cvs_video['video_name']]).unique()
    for video_name in unique_video_names:
        if pd.isna(video_name):
            continue  # Skip if video_name is NaN
        video_folder_name = video_name.rsplit('.mp4', 1)[0]
        video_folder_path = os.path.join(main_output_dir, video_folder_name)
        os.makedirs(video_folder_path, exist_ok=True)

        # Filter data for the current video_name
        df_frame_filtered = df_cvs_frame[df_cvs_frame['video_name'] == video_name].copy()
        df_video_filtered = df_cvs_video[df_cvs_video['video_name'] == video_name].copy()
        
        # Remove the 'video_name' column from filtered DataFrames
        df_frame_filtered.drop(columns=['video_name'], inplace=True)
        df_video_filtered.drop(columns=['video_name'], inplace=True)

        # Save to Excel without 'video_name' column
        df_frame_filtered.to_excel(os.path.join(video_folder_path, 'frame.xlsx'), index=False)
        df_video_filtered.to_excel(os.path.join(video_folder_path, 'video.xlsx'), index=False)


def main():
     # Setup command-line argument parsing
    parser = argparse.ArgumentParser(description='Process CVS annotations.')
    parser.add_argument('--input_file', required=True, help='Path to the input JSON file containing annotations')
    # parser.add_argument('--output_frame', required=True, help='Path to the output Excel file for frame level annotations')
    # parser.add_argument('--output_video', required=True, help='Path to the output Excel file for video level annotations')
    # parser.add_argument('--output_incomplete', required=True, help='Path to the output Excel file for incomplete annotations')
    args = parser.parse_args()
    
    # Call the process_annotations function with the parsed arguments
    process_annotations(args.input_file) # , args.output_frame, args.output_video, args.output_incomplete)


if __name__ == '__main__':
    main()
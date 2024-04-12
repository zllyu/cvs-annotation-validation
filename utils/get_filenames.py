import os

# input directory
directory_path = 'trim_videos_outputs/success/untrimmed'

# output file name
output_filename = 'success_untrimmed.txt'

with open(output_filename, 'w') as file:
    for name in os.listdir(directory_path):
        full_path = os.path.join(directory_path, name)
        if os.path.isfile(full_path) and name.endswith('.mp4'):
            file.write(name + '\n')

print(f'Saved to {output_filename}')

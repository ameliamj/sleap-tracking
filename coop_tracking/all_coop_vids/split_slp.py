import sleap_io as sio
import os

# Example usage:
# Replace with the path to your SLEAP project file
input_path = "/gpfs/radev/pi/saxena/aj764/Nina_Model_Testing/Fiber/labels.v001.slp" 
output_dir = "/gpfs/radev/pi/saxena/aj764/Nina_Model_Testing/"

# split_sleap_labels_by_video(input_slp_file, output_folder)

# def split_sleap_labels_by_video(input_path: str, output_dir: str):
"""
Splits a single SLEAP project file containing multiple videos into
separate project files, one for each video.

Args:
    input_path: Path to the combined .slp project file.
    output_dir: Directory where the new .slp files will be saved.
"""
# Load the main project file
try:
    labels = sio.load_file(input_path)
except Exception as e:
    print(f"Error loading {input_path}: {e}")

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Group labeled frames by video filename
labels_by_video = {}
for lf in labels.labeled_frames:
    video_filename = lf.video.filename
    if video_filename not in labels_by_video:
        labels_by_video[video_filename] = sio.Labels(
            videos=[lf.video],
            skeletons=labels.skeletons,
            tracks=labels.tracks
        )
    labels_by_video[video_filename].labeled_frames.append(lf)

# Save each video's labels to a new project file
for video_filename, video_labels in labels_by_video.items():
    base_name = os.path.splitext(os.path.basename(video_filename))[0]
    output_path = os.path.join(output_dir, f"{base_name}.slp")
    
    try:
        sio.save_file(video_labels, output_path)
        print(f"Successfully saved labels for video '{video_filename}' to '{output_path}'.")
    except Exception as e:
        print(f"Error saving labels for video '{video_filename}': {e}")



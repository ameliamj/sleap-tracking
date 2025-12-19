import sleap_io as sio
root = '/gpfs/radev/pi/saxena/aj764/Nina_Model_Testing/'

# Load your manual annotations and new predictions
base_labels = sio.load_file(root + "Red-Green/labels.v001.slp")
predictions = sio.load_file(root + "Collars/Red-Green/labels.v001.slp")

# Merge predictions into base project
# Default 'smart' strategy preserves manual labels
result = base_labels.merge(predictions)

# Check what happened
print(f"Frames merged: {result.frames_merged}")
print(f"Instances added: {result.instances_added}")

# Save the merged project
base_labels.save(root + "RG.slp")
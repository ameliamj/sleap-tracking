import sys
sys.path.append('../')

from src.classes.vid_loader import VidLoader 
from src.classes.pred_loader import PredLoader
from src.classes.job_loader import JobLoader

color_id = 'collar' # or 'dyed' these are the two options

# get all of the videos 
# vids = VidLoader(color_type=color_id, out=False)
# preds = PredLoader.from_vids(color_type=color_id, vid_loader=vids)
# only have to get preds from vid the first time to create df then can use:
# preds = PredLoader(color_id + '_preds_df.csv')
jobs = JobLoader(color_id + '_preds_df.csv', color_type=color_id)

inst = 'multi' # or 'single'
color_pair = 'GB' # can put None or leave blank for single inst
write = False # will write script to job directory specified in global utils

# for all color pairs you want to generate jobs for
job_commands = jobs.get_job_script(inst=inst, color_pair=color_pair, write=write)

# here you are running dsq jobs! then get the progress
jobs.get_progress(inst, color_pair)

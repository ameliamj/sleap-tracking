import sys
sys.path.append('../')

from src.classes.vid_loader import VidLoader 
from src.classes.pred_loader import PredLoader
from src.classes.job_loader import JobLoader

color_id = 'dyed' # or 'dyed' these are the two options

# get all of the videos 
# vids = VidLoader(color_type=color_id, out=False)
# preds = PredLoader.from_vids(color_type=color_id, vid_loader=vids)
# only have to get preds from vid the first time to create df then can use:
preds = PredLoader(color_id + '_preds_df.csv')

# Note: right now all the below functions will do the operation for the whole data 
# frame which is inefficent if you are doing preds in batchs (by color pair for instance)
# so you could wait till you have ALL preds before you run them or I could specify
# them color pair later on...

# get all of the initial and velocity nans for pred you just did
preds.get_nan()

# correct the predictions
# preds.correct()

# get the event ids for lever/mag events
# preds.get_event_ids()

# get the trial types for the test multi trials
# preds.get_trial_types()

# get the familiarity level for test multi trials
# preds.get_familiar()

# see if there is fiber pho data for the test multi trials
# preds.get_fiber_pho()

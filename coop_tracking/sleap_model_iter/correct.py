import sys
sys.path.append('../')

from utils.pred_loader import PredLoader

color_id = 'uncued' # or 'dyed' these are the two options

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
# print('getting nan')
# preds.get_nan()

# correct the predictions
# print('doing corrections')
# preds.correct()

# get the event ids for lever/mag events
print('getting event ids')
preds.get_event_ids()
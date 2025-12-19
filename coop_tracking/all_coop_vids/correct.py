import sys
sys.path.append('../')

import argparse
import h5py
import pandas as pd
from src.utils.global_utils import ROOTDIR
from src.utils.error_utils import  high_vel_nan, lowess_fill

parser = argparse.ArgumentParser(description="ex")
parser.add_argument("--video", type=str, default="", help="")

args = parser.parse_args()

df = pd.read_csv('all_coop_uncorrected.csv')
row = df[df['video'] == args.video].squeeze()

# load file
with h5py.File(ROOTDIR + f'{row['dir']}/{row['session']}/Tracking/h5_uncorrected/{row['video']}.predictions.h5','r') as f:
    locations = f["tracks"][:].T

# do corrections
locations = high_vel_nan(locations)
locations = lowess_fill(locations)

# save file
f = h5py.File(ROOTDIR + f'{row['dir']}/{row['session']}/Tracking/h5_corrected/{row['video']}.predictions.h5','r+')
f["tracks"][:] = locations.T
f.close()
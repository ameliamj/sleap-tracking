import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import h5py

from .global_utils import MAX_VEL, SMOOTHING, BAD_NAN
from .global_utils import ROOTDIR, TESTDIR, TRAINDIR, LADIR, BYDIR


# gets rid of any predictions of nodes that travel faster than max rat velocity
def high_vel_nan(locations):
    frames, nodes, _, rats = locations.shape
    for r in range(rats):
        for n in range(nodes):
            node_locs = locations[:, n, :, r]
            j = 0
            while np.sum(np.isnan(node_locs[j])) != 0 and j < (frames - 1): # make sure first node isn't nan
                j += 1
            k = j + 1
            while k < frames:
                if np.sum(np.isnan(node_locs[k])) == 0:
                    vel = np.sqrt(np.sum(np.square(node_locs[j] - node_locs[k]))) / (k - j)
                    if np.isnan(vel): 
                        print(j, node_locs[j])
                        print(k, node_locs[k])
                        print()
                    if (vel) > 200:
                        node_locs[k] = [np.nan, np.nan]
                        k += 1
                    else: 
                        j += 1 
                        while np.sum(np.isnan(node_locs[j])) != 0 and j < (frames - 1): # make sure j isn't nan
                            j += 1
                        k = j + 1
                else:
                    k += 1
                
    return locations        

# fills in nan values in locations with lowess smoothing
def lowess_fill(locations):
    frames, nodes, points, rats = locations.shape
    lowess = sm.nonparametric.lowess
    for r in range(rats):
        for n in range(nodes):
            node_locs = locations[:, n, :, r]
            for f in range(frames):
                for p in range(points):
                    if np.isnan(node_locs[f, p]):
                        if (f - SMOOTHING >= 0 and f + (SMOOTHING + 1) < frames): 
                            
                            endog = node_locs[f - SMOOTHING: f + (SMOOTHING + 1), p]
    
                            endog = np.concatenate((endog[:SMOOTHING], endog[SMOOTHING + 1:]))
                            exog = np.arange(0, (SMOOTHING * 2) + 1, 1) + (f - SMOOTHING)
                            exog = np.concatenate((exog[:SMOOTHING], exog[SMOOTHING + 1:]))
                            node_locs[f, p] = lowess(endog, exog, xvals=[f])  
    return locations        

# graphs the x and y position of the rats separately for the given node,
# from start frame to the end frame
def graph_locations(locations, node, start, end):
    fig, ax = plt.subplots(ncols=2, figsize=(10, 4))
    ax[0].plot(np.arange(start, end), locations[start:end, node, 0, ])
    ax[0].set_title("x pos over time")
    ax[0].set_xlabel("frames")
    ax[0].set_ylabel("x pos")
    ax[1].plot(np.arange(start, end), locations[start:end, node, 1, ])
    ax[1].set_title("y pos over time")
    ax[1].set_xlabel("frames")
    ax[1].set_ylabel("y pos")

# gets the percentage of predicted node locations that are nan
def get_nan_prec(locations):
    return np.sum(np.isnan(locations)) / np.prod(locations.shape)

# returns if the precentage of nan locations are over the abitrary threshold
# where we won't bother correcting them
def nan_good(initial_nan, vel_nan):
    return ((initial_nan < BAD_NAN) and (vel_nan - initial_nan < BAD_NAN))

# gets video and session name from a key/vid from VidLoader object
def get_vs(key, vid):
    sesh_split = key.split('/')
    v = vid[:-4]
    s = sesh_split[1]
    return v,s

# given a multi animal video and the possible cohorts it could be in 
# will return the cohort of each animal
def get_cohort(vid, cohorts):
    first_coh = None
    for coh in cohorts:
        if vid.count(coh) == 2:
            return (coh, coh)
        elif vid.count(coh) == 1:
            if first_coh is None:
                first_coh = coh
            else:
                return (first_coh, coh)
    print(vid)
    return (first_coh, None)

def get_color(vid, coh):
    parse = vid.replace('.', '_')
    parse = parse.split('_')
    coh_index = np.argmin([vid.find(coh[0]), vid.find(coh[1])])
    try:
        # animal_ids = [x for x in parse if x.startswith(coh[coh_index])][0]
        animal_ids = [x for x in parse if (coh[coh_index] in x)][0]
    except:
        print(vid)
    parsed_II = animal_ids.split('-')
    try:
        trial_color = [parsed_II[0][-1], parsed_II[1][-1]]
        trial_key = ''
        if 'R' in trial_color:
            trial_key += 'R'
        if 'G' in trial_color:
            trial_key += 'G'
        if 'Y' in trial_color:
            trial_key += 'Y'
        if 'B' in trial_color:
            trial_key += 'B'
    except:
        print(vid)
        trial_key = 'na'

    
    return trial_key

# given a row of the data frame from PredLoader, will load the h5 files and return 
# the predicted locations
def load_file(row):
    # tt = TESTDIR if row['test/train'] == 'test' else (TRAINDIR if row['test/train'] == 'train' else LADIR)
    # tt = tt if row['test/train'] != '1by1' else BYDIR
    tt = row['dir']
    session = row['session']
    vid = row['vid']
    try: 
        # if row['test/train'] == 'lg train':
        #      with h5py.File(ROOTDIR + tt + session + '/Tracking/h5/' + vid + 'predictions.h5','r') as f:
        #         locations = f["tracks"][:].T
        # else: 
        with h5py.File(ROOTDIR + tt + '/' + session + '/Tracking/h5/' + vid + '.predictions.h5','r') as f:
            locations = f["tracks"][:].T
        return locations
    except FileNotFoundError:
        # print(ROOTDIR + tt + '/' + session + '/Tracking/h5/' + vid + '.predictions.h5')
        return None

import os

# given a row of the data frame from PredLoader, will load the h5 files and return 
# the predicted locations
def load_file_fiber_redo(row):
    vid = row['vid']
    try: 
        with h5py.File(ROOTDIR + '/fiber_videos/pts/Tracking/h5/' + vid + '.h5','r') as f:
                locations = f["tracks"][:].T
        return locations
    except FileNotFoundError:
        return None


# given a row of the data frame from PredLoader and the corrected locations, will save
# the corrected locations over the old predicted locations
def save_file(row, locations):
    tt = TESTDIR if row['test/train'] == 'test' else (TRAINDIR if row['test/train'] == 'train' else LADIR)
    session = row['session']
    vid = row['vid']
    if row['test/train'] == 'lg train':
        f = h5py.File(ROOTDIR + tt+ session + '/Tracking/h5/' + vid + 'predictions.h5','r+')
    else:
        f = h5py.File(ROOTDIR + tt+ session + '/Tracking/h5/' + vid + '.predictions.h5','r+')
    f["tracks"][:] = locations.T
    f.close()
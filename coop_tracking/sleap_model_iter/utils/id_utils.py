import numpy as np
import pandas as pd
from .error_utils import load_file
from .global_utils import levx, lev1y, lev2y, mag1y, mag2y, magx, MAXDIST, SMOOTHING
from .global_utils import ROOTDIR, TESTDIR, TRAINDIR
import cv2

# given a row of the data frame from PredLoader, will add the rat id to each lever and mag
# event or return that a lever / mag file doesn't exist for this trial
def get_lever_mag(row, errors):
    
    tt = row['dir'] 
    behav = '/Behavioral/processed/'
    session = str(row['session'])
    vid = row['vid']
    if row['pred']:
        locations = load_file(row)

    # Load the video
    video_path = str(ROOTDIR + tt + session + '/Videos/' +  vid + '.mp4')
    cap = cv2.VideoCapture(video_path)
    # Get FPS
    fps = cap.get(cv2.CAP_PROP_FPS)
        
    lever_exists, mag_exists = True, False
    lev_error, mag_error = np.nan, np.nan
    try:
        lever = pd.read_csv(ROOTDIR + tt + session + behav + 'lever/' +  vid + '_lever.csv')
        if row['pred'] and locations is not None:
            lever, nan_count = get_rat_id(lever, locations, 'lever', fps)
            lever.to_csv(ROOTDIR + tt + session + behav + 'lever/' +  vid + '_lever.csv', index=False)
            # if nan_count > lever.shape[0] / 3 and row['correct'] == True:
            #     row['check'] = 'here'
                # print(row)
                # new_row = pd.DataFrame(row)
                # errors = pd.concat([errors, row], ignore_index=True)
            print(session, vid, 100 * np.sum(np.isnan(lever['RatID'])) / lever.shape[0], row['initial nan'])
            lev_error = 100 * np.sum(np.isnan(lever['RatID'])) / lever.shape[0]
        else:
            print(session, vid, 'locations is none')
    except FileNotFoundError:
        print(session, vid, 'cant find lever file')
        lever_exists = False
        
    try:
        mag = pd.read_csv(ROOTDIR + tt + session + behav + 'mag/' + vid + '_mag.csv')
        if  row['pred'] and locations is not None:
            try:
                mag, nan_count = get_rat_id(mag, locations, 'mag', fps)
                mag_error = 100 * np.sum(np.isnan(mag['RatID'])) / lever.shape[0]
            except:
                print('mag not working', row)
            mag.to_csv(ROOTDIR + tt + session + behav + 'mag/' +  vid + '_mag.csv', index=False)
            # if nan_count > mag.shape[0] / 3 and row['correct'] == True:
            #     row['check'] = 'here'
            #     errors = pd.concat([errors, row], ignore_index=True)
    except FileNotFoundError:
        mag_exists = False 
    
    return lever_exists, mag_exists, lev_error, mag_error
    
# for a given list of events and locations and event type (mag/lever), will add an 
# additional column to events that has the identity of which rat particapted in the 
# event given the rat locations
def get_rat_id(events, locations, event_type, fps):
    pad = 100
    x = locations[:, 0, 0, :].flatten()
    y = locations[:, 0, 1, :].flatten()
    
    # Adjust these depending on how aggressive you want to be
    low, high = 5, 95
    
    x_min, x_max = np.nanpercentile(x, [low, high])
    y_min, y_max = np.nanpercentile(y, [low, high])
    
    # Corners of the box
    bottom_left  = (x_min, y_min)
    top_right    = (x_max, y_max)
    top_left     = (x_min, y_max)
    bottom_right = (x_max, y_min)

    levx, magx = x_min, x_max
    lev2y, lev1y = y_min + (.25 * (y_max - y_min)), y_min + (.75 * (y_max - y_min))
    mag2y, mag1y = y_min + (.25 * (y_max - y_min)), y_min + (.75 * (y_max - y_min))

    
    ratID = []
    index_count = 0
    for row in events.itertuples(index=False):

        # check if there is an absolute time
        # check if absolute time is within the frame length
        # get both rat distances
            # see if either rat is close enough (check for nan values)
            # if both rats are close enough, check which one is closer

        ratNum = -1
        # is there an absolute time
        if np.isnan(row.AbsTime):
            ratNum = np.nan
            # print(index_count, 'abs time is nan')
        else:
            # calculate frame
            frame = int(row.AbsTime * fps)

            # make sure frame is within the range of locations
            if frame >= locations.shape[0]:
                ratNum = np.nan
                # print(index_count, 'frame out of range')
            else:
                # Get coordinates of both mice for the said frame
                ratpos1 = locations[frame, 0, :, 0]
                ratpos2 = locations[frame, 0, :, 1]
                
                # Calculate the distances
                if event_type == 'lever':
                    if row.LeverNum == 1:
                        distance1 = np.sqrt((ratpos1[0] - levx)**2 + (ratpos1[1] - lev1y)**2)
                        distance2 = np.sqrt((ratpos2[0] - levx)**2 + (ratpos2[1] - lev1y)**2)
                
                    elif row.LeverNum == 2:
                        distance1 = np.sqrt((ratpos1[0] - levx)**2 + (ratpos1[1] - lev2y)**2)
                        distance2 = np.sqrt((ratpos2[0] - levx)**2 + (ratpos2[1] - lev2y)**2)
                    else:
                        ratNum = np.nan #assign number for Nan values
                        # print(index_count, 'lever number is wrong')
                elif event_type == 'mag':
                    if row.MagNum == 1:
                        distance1 = np.sqrt((ratpos1[0] - magx)**2 + (ratpos1[1] - mag1y)**2)
                        distance2 = np.sqrt((ratpos2[0] - magx)**2 + (ratpos2[1] - mag1y)**2)
            
                    elif row.MagNum == 2:
                        distance1 = np.sqrt((ratpos1[0] - magx)**2 + (ratpos1[1] - mag2y)**2)
                        distance2 = np.sqrt((ratpos2[0] - magx)**2 + (ratpos2[1] - mag2y)**2)
                
                    else:
                        ratNum = np.nan #assign number for Nan values
                else:
                    raise Exception("not a valid event type (yikes)")
            
                if not np.isnan(ratNum):
                    if distance1 < MAXDIST and distance2 < MAXDIST:
                        ratNum = 0 if distance1 < distance2 else 1
                    elif distance1 < MAXDIST: # dist2 could be nan or non-plausible
                        ratNum = 0
                    elif distance2 < MAXDIST: # dist1 could be nan or non-plausible
                        ratNum = 1
                    else:
                        ratNum = np.nan # neither distance is valid or plausible
                        # print(index_count, 'neither rat is in range', distance1, distance2)
        
        # Add new element to the list
        ratID.append(ratNum)
        index_count += 1
    
    # Add new column to the dataframe
    events["RatID"] = ratID
    nan_count = events['RatID'].isna().sum()
    return events, nan_count


# for a given list of events and locations and event type (mag/lever), will add an 
# additional column to events that has the identity of which rat particapted in the 
# event given the rat locations
def get_rat_id_improved(events, locations, event_type):
    ratID = []
    ratConf = []
    for row in events.itertuples(index=False):

        # check if there is an absolute time
        # check if absolute time is within the frame length
        # get both rat distances
            # see if either rat is close enough (check for nan values)
            # if both rats are close enough, check which one is closer

        ratNum = -1
        # is there an absolute time
        if np.isnan(row.AbsTime):
            ratNum = np.nan
            conf = 0
        else:
            # calculate frame
            frame = int(row.AbsTime * fps)

            # make sure frame is within the range of locations
            if frame > locations.shape[0]:
                ratNum = np.nan
                conf = 0
            else:
                all_ratNum = []
                for i in range(SMOOTHING):
                    if frame + (i - (SMOOTHING // 2)) < locations.shape[0]:
                        # Get coordinates of both mice for the said frame
                        ratpos1 = locations[frame + (i - (SMOOTHING // 2)), 0, :, 0]
                        ratpos2 = locations[frame + (i - (SMOOTHING // 2)), 0, :, 1]
                        
                        # Calculate the distances
                        if event_type == 'lever':
                            if row.LeverNum == 1:
                                distance1 = np.sqrt((ratpos1[0] - levx)**2 + (ratpos1[1] - lev1y)**2)
                                distance2 = np.sqrt((ratpos2[0] - levx)**2 + (ratpos2[1] - lev1y)**2)
                        
                            elif row.LeverNum == 2:
                                distance1 = np.sqrt((ratpos1[0] - levx)**2 + (ratpos1[1] - lev2y)**2)
                                distance2 = np.sqrt((ratpos2[0] - levx)**2 + (ratpos2[1] - lev2y)**2)
                            else:
                                ratNum = np.nan #assign number for Nan values
                        elif event_type == 'mag':
                            if row.MagNum == 1:
                                distance1 = np.sqrt((ratpos1[0] - magx)**2 + (ratpos1[1] - mag1y)**2)
                                distance2 = np.sqrt((ratpos2[0] - magx)**2 + (ratpos2[1] - mag1y)**2)
                    
                            elif row.MagNum == 2:
                                distance1 = np.sqrt((ratpos1[0] - magx)**2 + (ratpos1[1] - mag2y)**2)
                                distance2 = np.sqrt((ratpos2[0] - magx)**2 + (ratpos2[1] - mag2y)**2)
                        
                            else:
                                ratNum = np.nan #assign number for Nan values
                        else:
                            raise Exception("not a valid event type (yikes)")
                    
                        if not np.isnan(ratNum):
                            if distance1 < MAXDIST and distance2 < MAXDIST:
                                ratNum = 0 if distance1 < distance2 else 1
                            elif distance1 < MAXDIST: # dist2 could be nan or non-plausible
                                ratNum = 0
                            elif distance2 < MAXDIST: # dist1 could be nan or non-plausible
                                ratNum = 1
                            else:
                                ratNum = np.nan # neither distance is valid or plausible

                        all_ratNum.append(ratNum)
                if np.mean(all_ratNum) == 0 or np.mean(all_ratNum) == 1:
                    # ideal case where prediction is consistent!
                    ratNum = np.mean(all_ratNum)
                    conf = 1
                else:
                    # non-idea case where there is disagreement / missing values
                    ratNum = round(np.nanmean(all_ratNum))
                    conf = len([x for x in all_ratNum if x == ratNum]) / len(all_ratNum)
        # Add new element to the list
        ratID.append(ratNum)
        ratConf.append(cont)
    
    # Add new column to the dataframe
    events["RatID"] = ratID
    events["IDConf"] = ratConf
    nan_count = events['RatID'].isna().sum()
    return events, nan_count
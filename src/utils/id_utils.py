import numpy as np
import pandas as pd
from .error_utils import load_file
from .global_utils import fps, levx, lev1y, lev2y, mag1y, mag2y, magx, MAXDIST, SMOOTHING
from .global_utils import ROOTDIR, TESTDIR, TRAINDIR

# given a row of the data frame from PredLoader, will add the rat id to each lever and mag
# event or return that a lever / mag file doesn't exist for this trial
def get_lever_mag(row, errors):

    # Method 1: Appending rows using pd.concat
    # new_row = pd.DataFrame([{'col1': 1, 'col2': 'A'}])
    # df = pd.concat([df, new_row], ignore_index=True)
    
    tt = TESTDIR if row['test/train'] == 'test' else TRAINDIR
    behav = '/Behavioral/processed/' if row['test/train'] == 'test' else '/Behavioral/'
    session = row['session']
    if row['test/train'] == 'test': 
        vid = row['vid']
    else:
        vid_temp = row['vid'].split('_')
        vid = vid_temp[0] + '_'  + vid_temp[3]
    if row['pred']:
        locations = load_file(row)
        
    lever_exists, mag_exists = True, True
    try:
        lever = pd.read_csv(ROOTDIR + tt + session + behav + 'lever/' +  vid + '_lever.csv')
        if row['pred']:
            lever, nan_count = get_rat_id(lever, locations, 'lever')
            lever.to_csv(ROOTDIR + tt + session + behav + 'lever/' +  vid + '_lever.csv', index=False)
            print(ROOTDIR + tt + session + behav + 'lever/' +  vid + '_lever.csv')
            if nan_count > lever.shape[0] / 3 and row['correct'] == True:
                row['check'] = 'here'
                print(row)
                # new_row = pd.DataFrame(row)
                errors = pd.concat([errors, row], ignore_index=True)
    except FileNotFoundError:
        lever_exists = False
        
    try:
        mag = pd.read_csv(ROOTDIR + tt + session + behav + 'mag/' + vid + '_mag.csv')
        if row['pred']:
            try:
                mag, nan_count = get_rat_id(mag, locations, 'mag')
            except:
                print(row)
            mag.to_csv(ROOTDIR + tt + session + behav + 'mag/' +  vid + '_mag.csv', index=False)
            if nan_count > mag.shape[0] / 3 and row['correct'] == True:
                row['check'] = 'here'
                errors = pd.concat([errors, row], ignore_index=True)
    except FileNotFoundError:
        mag_exists = False 
    return lever_exists, mag_exists, errors
    
# for a given list of events and locations and event type (mag/lever), will add an 
# additional column to events that has the identity of which rat particapted in the 
# event given the rat locations
def get_rat_id(events, locations, event_type):
    ratID = []
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
        else:
            # calculate frame
            frame = int(row.AbsTime * fps)

            # make sure frame is within the range of locations
            if frame > locations.shape[0]:
                ratNum = np.nan
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
            
        # Add new element to the list
        ratID.append(ratNum)
    
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
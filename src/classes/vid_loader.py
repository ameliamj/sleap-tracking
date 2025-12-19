import sys
sys.path.append('../../')

import os
import numpy as np
from src.utils.error_utils import get_color, get_cohort
from src.utils.global_utils import DYED_COHORTS, COLLAR_COHORTS
from src.utils.global_utils import ROOTDIR, TESTDIR, TRAINDIR


class VidLoader:
    # given cohorts and file path will create dictionaries of all videos in test and train directories
    # and split these videos into single and multi animal and into respective color pairs
    def __init__(self, color_type, cohorts=None, out=True):
        if not (color_type == 'dyed' or color_type == 'collar'):
            raise Exception("didn't specify a valid color type (dyed or collar). boo.")
            
        self.color_type = color_type # needs to be dyed or collar
        if cohorts is not None:
            self.cohorts = cohorts
        elif self.color_type == 'dyed':
            self.cohorts = DYED_COHORTS
        else: # self.color_type == 'collar':
            self.cohorts = COLLAR_COHORTS

        self.pts_single_vids, self.pts_multi_vids, self.tc_multi_vids = self.get_vids()
        self.pts_color_vids = self.get_color_vids(self.pts_multi_vids, 'test')        
        self.tc_color_vids = self.get_color_vids(self.tc_multi_vids, 'train')

        if out:
            self.print_output()

    # creates dictionaries that have all of the videos from PairedTestingSessions and 
    # Training_COOPERATION
    # NOTE: SPECIFICALLY ONLY FOR APRIL 2024 THROUGH NOVEMBER 2024, because these are the 
    # only vides with dye
    def get_vids(self):
        # get vids from paired testing session
        vid_subdirs = []
        for subdir, dirs, files in os.walk(ROOTDIR + TESTDIR):
            if subdir.endswith("Videos"):
                vid_subdirs.append(subdir)
        vid_subdirs = sorted(vid_subdirs)
        
        pts_single_vids = {}
        pts_multi_vids = {}
        for vids in vid_subdirs:
            files = os.listdir(vids)
            cut_vids = vids[len(ROOTDIR):]
            pts_single_vids[cut_vids] = []
            pts_multi_vids[cut_vids] = []
            for file in files:
                if file.endswith('.mp4') and self.in_date_range(file):
                    coh_count = 0
                    for coh in self.cohorts:
                        coh_count += file.count(coh) 
                    if coh_count == 2:
                        pts_multi_vids[cut_vids].append(file)
                    else:
                        pts_single_vids[cut_vids].append(file)
            if len(pts_single_vids[cut_vids]) == 0:
                pts_single_vids.pop(cut_vids)
            if len(pts_multi_vids[cut_vids]) == 0:
                pts_multi_vids.pop(cut_vids)

        # get vids from training cooperation
        vid_subdirs = []
        for subdir, dirs, files in os.walk(ROOTDIR + TRAINDIR):
            vid_subdirs.append(subdir)
        vid_subdirs = sorted(vid_subdirs)
        
        tc_multi_vids = {}
        for vids in vid_subdirs:
            files = os.listdir(vids)
            cut_vids = vids[len(ROOTDIR):]
            tc_multi_vids[cut_vids] = []
            if '020625_COOPTRAIN_LARGEARENA_NF020B-NF020Y_Camera4.mp4' in vids:
                continue # this is like on weird folder with some single animal vids, I'm ignoring it
            for file in files:
                if file.endswith('.mp4') and self.in_date_range(file):
                    
                    # coh_count = 0
                    # for coh in self.cohorts:
                    #     coh_count += file.count(coh) 
                    # if coh_count == 2:
                    #     tc_multi_vids[cut_vids].append(file)
                    # else:
                    #     print(cut_vids, file)
                        
                    tc_multi_vids[cut_vids].append(file)
            if len(tc_multi_vids[cut_vids]) == 0:
                tc_multi_vids.pop(cut_vids) 

        return pts_single_vids, pts_multi_vids, tc_multi_vids

    # reorgs all of the multi vids into a dictionary by the color pair in the multi vid
    def get_color_vids(self, multi_vids, trial_type):
        color_vids = {}
        for key, value in multi_vids.items():
            for vid in value:
                coh = get_cohort(vid, self.cohorts)
                trial_key = get_color(vid, coh)
                # trial_key = get_color(vid, trial_type)
                if trial_key not in color_vids.keys():
                    color_vids[trial_key] = []
                color_vids[trial_key].append(vid)
        return color_vids

    # prints out how many of each type of video there are
    def print_output(self):
        print(f'these are how many videos there are in {TESTDIR}')
        print(f'There are {self.get_num_vids(self.pts_single_vids)} single instance videos')
        print(f'There are {self.get_num_vids(self.pts_multi_vids)} multi instance videos')
        color_len = self.get_num_vids(self.pts_color_vids, color=True)
        print(f'There are {color_len} multi instance videos')

        print()
        
        print(f'these are how many videos there are in {TRAINDIR}')
        print(f'There are {self.get_num_vids(self.tc_multi_vids)} multi instance videos')
        color_len = self.get_num_vids(self.tc_color_vids, color=True)
        print(f'There are {color_len} multi instance videos')

    # makes sure the video is in the date range from April 2024 and November 2024 (non-inclusive) if dyed
    # or after this range if collar
    def in_date_range(self, file):
        month = int(file[:2])
        year = int(file[4:6])
        if self.color_type == 'dyed':
            return (month >= 4 and month < 11 and year == 24)
        else: #  self.color_type == 'collar':
            return ((month >= 11 and year == 24) or year == 25)
        

    # gets the nubmer of videos that are stored in the given vid dict
    @staticmethod
    def get_num_vids(vid_dict, color=False):
        if color:
            tot_len = 0
            for key, value in vid_dict.items():
                print(f'There are {len(value)} videos from {key} color pair')
                tot_len += len(value)
        else:
            tot_len = 0
            for key, value in vid_dict.items():
                tot_len += len(value)
        return tot_len        

    
import sys
sys.path.append('../../')

import os
import numpy as np
from src.utils.error_utils import get_color, get_cohort
from src.utils.global_utils import DYED_COHORTS, COLLAR_COHORTS
from src.utils.global_utils import ROOTDIR, LADIR




class LargeArena:
    def __init__(self, color_type='dyed'):
        if not (color_type == 'dyed' or color_type == 'collar'):
            raise Exception("didn't specify a valid color type (dyed or collar). boo.")
        self.color_type = color_type # needs to be dyed or collar
        
        vid_subdirs = []
        for subdir, dirs, files in os.walk(ROOTDIR + LADIR):
            vid_subdirs.append(subdir)
        vid_subdirs = sorted(vid_subdirs)
        
        self.lg_vids = {}
        for vids in vid_subdirs:
            files = os.listdir(vids)
            cut_vids = vids[len(ROOTDIR):]
            self.lg_vids[cut_vids] = []
            for file in files:
                if file.endswith('.mp4'):
                    self.lg_vids[cut_vids].append(file)
            if len(self.lg_vids[cut_vids]) == 0:
                self.lg_vids.pop(cut_vids)
        

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

    
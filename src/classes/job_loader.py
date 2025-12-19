# need to define centroid and topdown, should be dicts where (color_type, color_pair) is the key!
import sys
sys.path.append('../../')

import os
import pandas as pd
from src.utils.error_utils import load_file
from src.utils.global_utils import CENTROID, TOPDOWN, SINGLE
from src.utils.global_utils import ROOTDIR, TESTDIR, TRAINDIR, JOBDIR, LADIR, BYDIR

class JobLoader:

    def __init__(self, filename, color_type):
        self.df = pd.read_csv(filename)
        self.color_type = color_type
        self.filename = filename

    def get_undone_vids(self, inst, color_pair=None):
        # only try to update the rows that don't have a prediction
        undone = self.df[self.df['pred'] == False]
        for index, row in undone.iterrows():
            locations = load_file(row)
            if locations is not None:
                self.df.at[index, 'pred'] = True
        self.df.to_csv(self.filename, index=False)
        # filter by instance and color pair    
        subset = self.df[(self.df['single/multi'] == inst)]
        if inst == 'multi' and color_pair is not None:
            if color_pair == 'fiber pho':
                subset = subset[(subset['fiber pho'])]
            else:
                subset = subset[(subset['color pair'] == color_pair)]
        run = subset[subset['pred'] == False]
        return run, subset

    def get_job_script(self, inst, color_pair=None, write=False, redo=False):
        if redo:
            subset = self.df[(self.df['single/multi'] == inst)]
            if inst == 'multi' and color_pair is not None:
                if color_pair == 'fiber pho':
                    run = subset[(subset['fiber pho'])]
                else:
                    run = subset[(subset['color pair'] == color_pair)]          
        else:
            run, _ = self.get_undone_vids(inst, color_pair) 

        start_command = f'module load miniconda; conda activate sleap; cd {ROOTDIR};'
        command_lines = ''
        for index, row in run.iterrows():
            tt = TESTDIR if row['test/train'] == 'test' else (TRAINDIR if row['test/train'] == 'train' else LADIR)
            tt = BYDIR if row['test/train'] == '1by1' else tt
            output_path = ROOTDIR + tt + str(row['session']) + '/Tracking' if color_pair != 'fiber pho' else ROOTDIR + tt + str(row['session']) + '/Tracking_Fiber'
            # makes directory for tracking output if not already made
            if not os.path.isdir(output_path):
                os.mkdir(output_path)
            if not os.path.isdir(output_path + '/slp'):
                os.mkdir(output_path + '/slp')
            if not os.path.isdir(output_path + '/h5'):
                os.mkdir(output_path + '/h5')

            if row['test/train'] == 'test':
                video_path = ROOTDIR + tt + row['session'] + '/Videos/' + row['vid'] + '.mp4'
            else:
                video_path = ROOTDIR + tt + row['session'] + '/' + row['vid'] + '.mp4'
            output_file = row['vid'] + '.predictions.'

            if inst == 'single':
                model = SINGLE
                track_command = f'sleap-track "{video_path}" --first-gpu -o "{output_path + '/slp/' + output_file + 'slp'}" -m "{model}"/'
            else:
                model_type = self.color_type if self.color_type != 'by' else 'collar'
                centroid_model = CENTROID[(model_type, color_pair)]
                topdown_model = TOPDOWN[(model_type, color_pair)]
    
                track_command = f'sleap-track "{video_path}" --first-gpu -o "{output_path + '/slp/' + output_file + 'slp'}" -m "{centroid_model}" -m "{topdown_model}"'
            convert_command = f'; sleap-convert --format analysis -o "{output_path + '/h5/' + output_file + 'h5'}" "{output_path + '/slp/' + output_file + 'slp'}"'
            command_lines += (start_command + track_command + convert_command + '\n')

        if write:
            if not os.path.isdir(JOBDIR): 
                os.mkdir(JOBDIR)
            with open(f"{JOBDIR}/{color_pair}_vids_job.txt", "w") as file:
                file.write(command_lines) 
        return command_lines

    def get_progress(self, inst, color_pair=None):
        undone, subset = self.get_undone_vids(inst, color_pair)
        per_done = round(((subset.shape[0] - undone.shape[0]) / subset.shape[0]) * 100, 2)
        print(f'{per_done}% of videos from {color_pair} have been tracked ({subset.shape[0] - undone.shape[0]} tracked videos, {undone.shape[0]} untracked videos)')
        
        
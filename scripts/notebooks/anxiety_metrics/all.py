import pandas as pd
import h5py
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from utils import get_dist

df = pd.read_csv('large_arena_preds_df.csv')

df = df[df['pred'] == True]

for index, row in df.iterrows():
    if index == 0:
        continue
    animal_id = row['vid'].split('_')[3]
    df.at[index, 'animal id'] = animal_id

    month, day, year = row['session'][:2], row['session'][2:4], row['session'][4:6]
    df.at[index, 'month'] = month
    df.at[index, 'day'] = day
    df.at[index, 'year'] = year

unique_ids = set(df['animal id'])

id_dates = {}
for ids in unique_ids:
    id_df = df[df['animal id'] == ids]
    id_df = id_df.sort_values(by=['year', 'month', 'day'])

    first_date = str(id_df.head(1)['session']).split()[1]
    last_date = str(id_df.tail(1)['session']).split()[1]

    id_dates[ids] = (first_date, last_date)

methods = ['wall', 'corner', 'center']
for method in methods:
    center_df = pd.DataFrame(columns=['animal id', 'first date', 'last date'])
    ind = 0
    for animal_id, values in id_dates.items():
        center_df.at[ind, 'animal id'] = animal_id
        
        for i, date in enumerate(values):
            row = df[(df['animal id'] == animal_id) & (df['session'] == date)]
            session = str(row['session']).split()[1]
            vid = str(row['vid']).split()[1]
            with h5py.File(f'/gpfs/radev/pi/saxena/aj764/Training_LARGEARENA_Individual/{session}/Tracking/h5_not_corrected/' + vid + 'predictions.h5','r') as f:
                locations = f["tracks"][:].T
                node_names = [n.decode() for n in f["node_names"][:]]
            
            center_time, not_center_time, nan_time, norm_center, norm_not_center = get_dist(method, locations) # CHANGE HERE!!
            if i == 0:
                center_df.at[ind, 'first center'] = center_time
                center_df.at[ind, 'first not center'] = not_center_time
                center_df.at[ind, 'first nan'] = nan_time
                center_df.at[ind, 'first norm center'] = norm_center
                center_df.at[ind, 'first norm not center'] = norm_not_center
                center_df.at[ind, 'first date'] = date
                center_df.at[ind, 'first nose'] = np.sum(np.isnan(locations[:, 0, :, :])) / np.prod(locations[:, 0, :, :].shape)
                center_df.at[ind, 'first head'] = np.sum(np.isnan(locations[:, 3, :, :])) / np.prod(locations[:, 3, :, :].shape)
            else:
                center_df.at[ind, 'last center'] = center_time
                center_df.at[ind, 'last not center'] = not_center_time
                center_df.at[ind, 'last nan'] = nan_time
                center_df.at[ind, 'last norm center'] = norm_center
                center_df.at[ind, 'last norm not center'] = norm_not_center
                center_df.at[ind, 'last date'] = date
                center_df.at[ind, 'last nose'] = np.sum(np.isnan(locations[:, 0, :, :])) / np.prod(locations[:, 0, :, :].shape)
                center_df.at[ind, 'last head'] = np.sum(np.isnan(locations[:, 3, :, :])) / np.prod(locations[:, 3, :, :].shape)
    
        ind += 1        
    
    labels = ['first date', 'last date']
    colors = ['tab:blue', 'tab:green']
    fig, ax = plt.subplots()
    ax.set_ylabel(f'percent of time spent in the {method} (%)')
    bplot = ax.boxplot([center_df[f'first center'], center_df[f'last center']], patch_artist=True, tick_labels=labels)
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)
    
    t_stat, p_value = stats.ttest_ind(center_df[f'first center'].astype(float), center_df[f'last center'].astype(float))
    x1, x2 = 1, 2
    y, h = 85, 2 
    plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, color='k')
    # plt.text((x1+x2)*.5, y+h, 'p value = ' + "{:.8f}".format(float(p_value)), ha='center', va='bottom', color='k')
    plt.text((x1+x2)*.5, y+h, 'p value = ' + str(p_value), ha='center', va='bottom', color='k')
    plt.title(f'time spend in {method}, not normalized')
    
    plt.show()
    plt.savefig(f'graphs/non-normal-{method}.png')
    
    labels = ['first date', 'last date']
    colors = ['tab:blue', 'tab:green']
    fig, ax = plt.subplots()
    ax.set_ylabel(f'percent of time spent in the {method} (%)')
    bplot = ax.boxplot([center_df[f'first norm center'], center_df[f'last norm center']], patch_artist=True, tick_labels=labels)
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)
    
    t_stat, p_value = stats.ttest_ind(center_df['first norm center'].astype(float), center_df['last norm center'].astype(float))
    x1, x2 = 1, 2
    y, h = 85, 2 
    plt.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, color='k')
    # plt.text((x1+x2)*.5, y+h, 'p value = ' + "{:.8f}".format(float(p_value)), ha='center', va='bottom', color='k')
    plt.text((x1+x2)*.5, y+h, 'p value = ' + str(p_value), ha='center', va='bottom', color='k')
    plt.title(f'time spend in {method}, normalized')
    
    plt.show()
    plt.savefig(f'graphs/normal-{method}.png')
             
    

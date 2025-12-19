import numpy as np
import matplotlib.pyplot as plt

def get_dist_frames(method, locations, node):
    if method == 'wall':
        return get_per_walls(locations, node=node)
    elif method == 'corner':
        return get_per_corners(locations, node=node)
    else:
        return get_per_center(locations, node=node)

def find_walls(locations, node):
    # find walls
    xmin, xmax = np.nanmin(locations[:, node, 0, :]), np.nanmax(locations[:, node, 0, :])
    ymin, ymax = np.nanmin(locations[:, node, 1, :]), np.nanmax(locations[:, node, 1, :])
    sides = [xmin, xmax, ymin, ymax]
    # find center
    center_x, center_y = ((xmax - xmin) / 2) + xmin, ((ymax - ymin) / 2) + ymin
    return sides, center_x, center_y

def calc_final_vals(dists, maxdist, locations, node):
    # by the center value
    in_area = [i for i,x in enumerate(dists) if x < maxdist and not np.isnan(x)]
    not_area = [i for i,x in enumerate(dists) if x > maxdist and not np.isnan(x)]
    nan_vals = [i for i,x in enumerate(dists) if np.isnan(x)]
    
    area_time = round(100 * len(in_area) / len(dists), 2)
    not_area_time = round(100 * len(not_area) / len(dists), 2)
    nan_time = round(100 * len(nan_vals) / len(dists), 2)

    # norm_area = 100 * (area_time / (area_time + not_area_time))
    # norm_not_area = 100 * (not_area_time / (area_time + not_area_time))

    
    # plt.plot(locations[not_area, node, 0, :], locations[not_area, node, 1, :], '.')
    # plt.plot(locations[in_area, node, 0, :], locations[in_area, node, 1, :], '.')
    # plt.gca().set_aspect("equal")
    # plt.show()
    
    return in_area

def get_per_center(locations, maxdist=200, node=0):
    
    sides, center_x, center_y = find_walls(locations, node)

    # get dist from center
    center_dist = np.sqrt((locations[:, node, 0, 0] - center_x)**2 + (locations[:, node, 1, 0] - center_y)**2)

    # by the center value
    return calc_final_vals(center_dist, maxdist, locations, node)

def get_per_walls(locations, maxdist=100, node=0):
    
    sides, center_x, center_y = find_walls(locations, node)
   
    # get dist from walls
    wall_dist = -1 * np.ones((locations.shape[0], 4))
    for i, s in enumerate(sides):
        if i < 2:
            wall_dist[:, i] = np.abs(locations[:, node, 0, 0] - s)
        else:
            wall_dist[:, i] = np.abs(locations[:, node, 1, 0] - s)
    
    min_wall_dist = np.min(wall_dist, axis=1)

    return calc_final_vals(min_wall_dist, maxdist, locations, node)

def get_per_corners(locations, maxdist=150, node=0):
    sides, center_x, center_y = find_walls(locations, node)
    
    corner_dist = -1 * np.ones((locations.shape[0], 4))

    i = 0
    for x in sides[:2]:
        for y in sides[2:]:
            corner_dist[:, i] = np.sqrt((locations[:, node, 0, 0] - x) ** 2 + (locations[:, node, 1, 0] - y) ** 2)
            i += 1
    
    min_corner_dist = np.min(corner_dist, axis=1)

    return calc_final_vals(min_corner_dist, maxdist, locations, node)

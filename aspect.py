import numpy as np

import matplotlib.pyplot as plt

import sys, glob
import h5py

import seaborn as sns

def index_to_zyx(index):
    ny, nx = 600, 1728
    z = index // (ny*nx)
    index = index % (ny*nx)
    y = index // nx
    x = index % nx
    return (z, y, x)

def find_aspect_ratio():
    cloudtracker = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5/'
    file_list = glob.glob("%s/clouds_*.h5" % cloudtracker)
    file_list.sort()

    file = h5py.File(file_list[60])
    keys = list(file.keys())
    keys.sort()

    for id in keys:
        if id == "-1": continue # noise
        z, y, x = index_to_zyx(np.array(np.hstack([
                        file['%s/%s' % (str(id), 'core')][...],
                        file['%s/%s' % (str(id), 'core_shell')]
                        ])))

        z_unique = np.unique(z)
        if len(z_unique) < 2: continue
        area = np.zeros(len(z_unique))

        for n, k in enumerate(z_unique):
            mask = (z == k)
            area[n] = np.float_(mask.sum() * 50. * 50.)

        thickness = (np.max(z_unique) - np.min(z_unique) + 1) * 50.
        aspect = thickness / np.sqrt(np.max(area))

        print("id: %6s, thickness = %3d, max_area = %8d, aspect ratio = %f" \
            % (id, thickness/50, np.max(area)/2500, aspect))

    # top_height = []
    # bottom_height = []
    # for i in range(180):
    #     file = h5py.File(file_list[i])
    #     keys = list(file.keys())
    #     keys.sort()

    #     for key in keys:
    #         z, y, x = index_to_zyx(np.array(file['%s/core' % key])) 

    #         if len(z) == 0: continue
    #         k = np.unique(z)
    #         max_k = max(k)
    #         min_k = min(k)
    #         top_height += [max_k]
    #         bottom_height += [min_k]


if __name__ == '__main__':
    find_aspect_ratio()

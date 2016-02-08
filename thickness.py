import numpy as np

import matplotlib.pyplot as plt

import sys, glob
import h5py

import seaborn as sns

def index_to_zyx(index):
    ny, nx = 300, 1728
    z = index // (ny*nx)
    index = index % (ny*nx)
    y = index // nx
    x = index % nx
    return (z, y, x)

def get_cloud_thickness():
    cloudtracker = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5/'
    file_list = glob.glob("%s/clouds_*.h5" % cloudtracker)
    file_list.sort()

    top_height = []
    bottom_height = []
    for i in range(180):
        file = h5py.File(file_list[i])
        keys = list(file.keys())
        keys.sort()

        for key in keys:
            z, y, x = index_to_zyx(np.array(file['%s/core' % key])) 

            if len(z) == 0: continue
            k = np.unique(z)
            max_k = max(k)
            min_k = min(k)
            top_height += [max_k]
            bottom_height += [min_k]
            
    top_heights = np.array(top_height)
    bot_heights = np.array(bottom_height)
    np.save('npy/top_height.npy', top_heights)
    np.save('npy/bot_height.npy', bot_heights)

def plot_cloud_thickness():
    top_height = np.load('npy/top_height.npy')
    bot_height = np.load('npy/bot_height.npy')
    top_height = top_height
    bot_height = bot_height

    thickness = (top_height - bot_height)

    tracked_h, x = np.histogram(thickness, bins=40, range=(0, 200), normed=False)

    print(tracked_h)
    print(min(thickness), np.mean(thickness), max(thickness))

    sns.set(rc={"figure.figsize": (4, 3)})
    plt.plot(x[1:], tracked_h)
    plt.title("Cloud core top heights")
    plt.ylabel("# Cloud cores")
    plt.xlabel("Altitude (levs)")

    plt.savefig('png/%s.png' % ('thickness'), bbox_inches='tight', dpi=300, \
        facecolor='w', transparent=True)


if __name__ == '__main__':
    # get_cloud_thickness()
    plot_cloud_thickness()

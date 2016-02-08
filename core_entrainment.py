import numpy as np

import sys, glob
from netCDF4 import Dataset as nc
import h5py

import matplotlib.pyplot as plt
import seaborn as sns

def index_to_zyx(index):
    ny, nx = 600, 1728
    z = index // (ny*nx)
    index = index % (ny*nx)
    y = index // nx
    x = index % nx
    return (z, y, x)


def get_core_entrainment():
    cloudtracker = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5/'
    file_list = glob.glob("%s/clouds_*.h5" % cloudtracker)
    file_list.sort()

    data = glob.glob("/newtera/loh/data/GATE/core/*.nc")
    data.sort()

    core_entrainment = []
    core_k = np.empty(280)
    core_k_count = np.zeros(280)
    for i in range(60, 62):
        print(i)

        file = h5py.File(file_list[i])
        keys = list(file.keys())
        keys.sort()

        eps = nc(data[i]).variables['ETETCOR'][:, 300:900, :]

        for key in keys:
            if key == -1: continue # Filter out noise
            if len(file['%s/core' % key]) < 18: continue
            z, y, x = index_to_zyx(np.array(file['%s/core' % key])) 

            for k in np.unique(z):
                core = np.nansum(eps[k, y[z == k], x[z == k]]) * 2500.

                if (core > 0.) & (core < 1.e2):
                    core_k[k] += core
                    core_k_count[k] += 1

    core_k = core_k / core_k_count
        
    np.save('npy/core.npy', np.array(core_k))


def plot_core_entrainment():
    core = np.load('npy/core.npy')
    
    core[(core < 0.) | (core > 1.e10)] = 0
    print(core)

    z = (np.arange(280)*50.+12.5)/1000.

    sns.set(rc={"figure.figsize": (4, 3)})
    # ax = sns.distplot(tracked_h)
    plt.plot(core, z)
    plt.title("GATE Cloud Core Properties")
    plt.ylabel("Height (km)")
    plt.xlabel("eps")

    plt.savefig('%s.png' % ('output'), bbox_inches='tight', dpi=300, \
        facecolor='w', transparent=True)


if __name__ == '__main__':
    get_core_entrainment()
    plot_core_entrainment()

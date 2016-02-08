import matplotlib.pyplot as plt
import numpy as np

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

def get_lifetime():
    file_list = glob.glob("../cloudtracker/cloudtracker/hdf5/h5/clouds_*.h5")
    file_list.sort()
    
    clouds = np.zeros(8000)
    for i in range(50):
        file = h5py.File(file_list[i])
        keys = list(file.keys())
        keys.sort()

        for key in keys:
            try:
                clouds[int(key)] += 1
            except:
                print(key, " error")
            
    np.save('npy/cloud_lifetime.npy', clouds)

def plot_lifetime():
    cloud_lifetime = np.load('npy/cloud_lifetime.npy')

    cloud_lifetime, x = np.histogram(cloud_lifetime, bins=15, range=(1, 15), normed=False)
    print(cloud_lifetime)

    sns.set(rc={"figure.figsize": (4, 3)})
    # ax = sns.distplot(tracked_h)
    plt.plot(cloud_lifetime)
    plt.title("Cloud core lifetime")
    plt.xlabel("Lifetime (min)")
    plt.ylabel("# Cloud cores")
    # plt.show()

    plt.savefig('%s.png' % ('output'), bbox_inches='tight', dpi=300, \
        facecolor='w', transparent=True)

if __name__ == '__main__':
    get_lifetime()
    plot_lifetime()
    
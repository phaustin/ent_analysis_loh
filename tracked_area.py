import numpy as np

import sys, glob
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

# if __name__ == '__main__':
#     file_list = glob.glob("../cloudtracker/cloudtracker/hdf5/clouds_*.h5")
#     file_list.sort()

#     area = []
#     for i in range(50):
#         file = h5py.File(file_list[i])
#         keys = list(file.keys())
#         keys.sort()

#         for key in keys:
#             area += [len(file['%s/core' % key])]
        
#     tracked_area = np.array(area)
#     np.save('npy/tracked_area.npy', tracked_area)

# Projected area
def get_tracked_area():
    cloudtracker = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5/'
    file_list = glob.glob("%s/clouds_*.h5" % cloudtracker)
    file_list.sort()

    area = []
    for i in range(180):
        file = h5py.File(file_list[i])
        keys = list(file.keys())
        keys.sort()

        for key in keys:
            if key == -1: continue # Filter out noise
            z, y, x = index_to_zyx(np.array(file['%s/core' % key])) 

            if len(z) == 0: continue
            k = np.unique(z, return_counts=True)
            max_k = (k[0][k[1] == (max(k[1]))])[0]
            area += [len(z == max_k)]
            
    tracked_area = np.array(area)
    np.save('npy/tracked_area.npy', tracked_area)


def plot_tracked_area():
    tracked_area = np.load('npy/tracked_area.npy')
    tracked_l = np.sqrt(tracked_area * 50 * 50)

    tracked_h, x = np.histogram(tracked_l, bins=40, range=(50, 2e3), normed=False)
    print(tracked_h)
    print(min(tracked_l), np.mean(tracked_l), max(tracked_l))

    sns.set(rc={"figure.figsize": (4, 3)})
    # ax = sns.distplot(tracked_h)
    plt.plot(tracked_h)
    plt.title("Projected (shallow) cloud core area")
    plt.xlabel("Area (m2)")
    plt.ylabel("# Cloud cores")
    # plt.show()

    plt.savefig('png/%s.png' % ('tracked_area'), bbox_inches='tight', dpi=300, \
        facecolor='w', transparent=True)


if __name__ == '__main__':
    # get_tracked_area()
    plot_tracked_area()

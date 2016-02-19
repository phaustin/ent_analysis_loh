import numpy as np

from netCDF4 import Dataset as nc
import matplotlib.pyplot as plt

import sys, glob
import h5py

import seaborn as sns

if __name__ == '__main__':
    id_list = list(range(180))

    cloud_lifetime = {}
    nn = 0
    for n in range(0, 180, 1):
        nc_file = nc('%s/%s_profile_%08d.nc' % ('cdf', 'core', n))
        id_list[nn] = list(nc_file.variables['ids'][:].astype(np.int))

        nn += 1

    for t, n in enumerate(id_list):
        for id in n:
            if id == -1: continue
            if str(id) in cloud_lifetime:
                cloud_lifetime[str(id)] += [t]
            else:
                cloud_lifetime[str(id)] = [t]

    cloud_l = []
    for item in cloud_lifetime:
        if len(cloud_lifetime[item]) < 2: continue
        cloud_l += [len(cloud_lifetime[item])]

    # l = 0
    # for item in cloud_lifetime:
    #     if len(cloud_lifetime[item]) > 10:
    #         print(item, cloud_lifetime[item])
    #         l += 1
    # print("%d clouds" % l)g

    bins = np.linspace(0, 20, 20)
    cloud_h, x = np.histogram(cloud_l, bins=bins, normed=False)

    bin_x = (x[1:] + x[:-1])/2.

    fig = plt.figure(1, figsize=(5, 3.125))
    fig.clf()
    ax = fig.add_subplot(111)
    
    plt.plot(bin_x, cloud_h)

    plt.savefig('%s.png' % ('output'), \
        bbox_inches='tight', dpi=300, facecolor='w', transparent=True)

import numpy as np
import glob, os, sys
sys.path.append('lib/')

from netCDF4 import Dataset as nc
import h5py
# from pylab import *

import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
import seaborn as sns

def index_to_zyx(index):
    z = index / (ny*nx)
    index = index % (ny*nx)
    y = index / nx
    x = index % nx
    return np.array((z, y, x))

def tracking_snapshot():
    fig = plt.figure(1, figsize=(8, 3))
    fig.clf()
    ax = fig.add_subplot(111)

    core = np.zeros((ny, nx), dtype=int)

    cloudtracker = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5/'
    file = '%s/clouds_00000000.h5' % cloudtracker
    with h5py.File(file, 'r') as f:
        keys = np.array(list(f.keys()), dtype=int)
        keys.sort()
        ids = 0

        core = []
        core_list = []
        for id in keys[:]:
            K, J, I = np.array(index_to_zyx(f['%s/condensed' % id][...]), dtype=int) 
            mask = (K >= 20) & (K <= 40)
            mask = mask & ((len(K) + len(J) + len(I)) > 24)
            core.append((J[mask], I[mask]))

    for id in range(len(core)):
        temp_mesh = np.zeros((ny, nx), dtype=int)

        # print id
        
        J, I = core[id][0], core[id][1]
        temp_mesh[J, I] = id

        palette = sns.color_palette("bright", len(core), desat=0.85)
        line_color = palette[id]
        line_color = '#%02x%02x%02x' % (int(line_color[0]*255), int(line_color[1]*255), int(line_color[2]*255))
        plt.contour(x, y, temp_mesh, levels=[0], colors=line_color, linewidths = (.4,),)

    # levs = np.linspace(1e-7, 2e-2, 11)
    # levs = array((1e-7, 1e-3, 5e-3, 1e-2, 2e-2))
    # cols = np.linspace(.8,0,5)
    # cols = [str(item) for item in cols]
    
    # plt.contourf(x, y, eps, levels=levs, colors=cols)
    # plt.colorbar()

    plt.title('Cloud snapshot between 1-2 km')
    plt.ylabel('y (km)')
    plt.xlabel('x (km)')

    plt.savefig('png/%s.png' % ('map_cloud_id'), bbox_inches='tight', dpi=300, \
        facecolor='w', transparent=True)

if __name__ == '__main__':
    nx = 1728
    ny = 600
    nz = 280

    dx = 50

    x = (np.arange(nx)*dx+12.5)/1000.
    y = (np.arange(ny)*dx+12.5)/1000.

    tracking_snapshot()
    print('Snapshot generated!')

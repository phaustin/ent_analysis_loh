import numpy as np
import glob, os, sys

# from netCDF4 import Dataset as nc
import h5py

import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

from scipy.interpolate import griddata
from matplotlib import cm
from matplotlib.colors import LightSource

def index_to_zyx(index):
    ny, nx = 600, 1728
    z = index // (ny*nx)
    index = index % (ny*nx)
    y = index // nx
    x = index % nx
    return np.array((z, y, x))

if __name__ == '__main__':
    fig = plt.figure(1, figsize=(8, 3))
    fig.clf()
    ax = fig.add_subplot(111, projection='3d')

    id = 29908

    cloudtracker = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5/'
    f = h5py.File('%s/clouds_%08d.h5' % (cloudtracker, 60))

    core = np.hstack([f['%s/core' % str(id)][...], f['%s/core_shell' % str(id)][...]])
    Z, Y, X = np.array(index_to_zyx(core), dtype=int) 

    mask = (Y > 200) & (Y < 400) & (Z < 200)
    Z = Z[mask]
    Y = Y[mask]
    X = X[mask]

    # Z, Y, X = zip(*sorted(zip(Z, Y, X)))

    ax = Axes3D(plt.figure())

    # X = np.array(X)
    # Y = np.array(Y)
    # Z = np.array(Z)

    # z = Z
    # y = Y
    # x = X

    # xi = np.linspace(min(x), max(x))
    # yi = np.linspace(min(y), max(y))
    # X, Y = np.meshgrid(xi, yi)
    # # interpolation
    # Z = griddata(x, y, z, xi, yi, interp='linear')

    xi = np.linspace(X.min(),X.max(),100)
    yi = np.linspace(Y.min(),Y.max(),100)
    # VERY IMPORTANT, to tell matplotlib how is your data organized
    zi = griddata((X, Y), Z, (xi[None,:], yi[:,None]), method='cubic')

    CS = plt.contour(xi,yi,zi,40, linewidths=.75, cmap=plt.cm.get_cmap('cubehelix_r'))
    # ax = fig.add_subplot(1, 2, 2, projection='3d')

    xig, yig = np.meshgrid(xi, yi)
    ax.contour3D(xig, yig, zi, cmap=plt.cm.get_cmap('RdYlBu'))

    # k = np.unique(Z)
    # # ax.plot_surface(X, Y, Z, rstride=1, cstride=1)

    # ls = LightSource(270, 45)
    # rgb = ls.shade(Z, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
    # surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, facecolors=rgb,
    #                        linewidth=0, antialiased=False, shade=False)

    # ax.contour3D(X, Y, Z, cmap=plt.cm.get_cmap('RdYlBu'))

    plt.savefig('%s.png' % ('output'), bbox_inches='tight', dpi=300, \
        facecolor='w', transparent=True)


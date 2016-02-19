import numpy as np
import glob, os, sys

from netCDF4 import Dataset as nc
import h5py

import matplotlib
matplotlib.use('Agg')

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

cp = 1004.    # Heat capacity at constant pressure for dry air [J kg^-1 K^-1]
cpv = 1870.    # Heat capacity at constant pressure of water vapor [J kg^-1 K^-1]
Cl = 4190.     # Heat capacity of liquid water [J kg^-1 K^-1]
Rv = 461.      # Gas constant of water vapor [J kg^-1 K^-1]
Rd = 287.      # Gas constant of dry air [J kg^-1 K^-1]
Lv = 2.5104e6 # Latent heat of vaporization [J kg^-1]
Lf = 0.3336e6  # Latent heat of fusion [J kg^-1]
Ls = 2.8440e6  # Latent heat of sublimation [J kg^-1]
g = 9.81       # Accelleration of gravity [m s^-2]
p_0 = 100000.
epsilon = Rd/Rv
lam = Rv/Rd - 1.
lam = 0.61


def h(T, z, qn, qi):
    return cp*T + g*z - Lv*qn - Ls*qi

def mse(data, k, j, i):
    return h(data['TABS'][k, j, i],
                 data['z'][k, np.newaxis, np.newaxis],
                 data['QN'][k, j, i]/1000.,
                 data['QI'][k, j, i]/1000.)

def index_to_zyx(index):
    ny, nx = 600, 1728
    z = index // (ny*nx)
    index = index % (ny*nx)
    y = index // nx
    x = index % nx
    return np.array((z, y, x))

def main():
    id = 29908
    n = 60

    fig = plt.figure(1, figsize=(5, 4))
    fig.clf()

    HDF5 = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5/'
    cloud_file = h5py.File('%s/clouds_%08d.h5' % (HDF5, n))
    core_index = np.hstack([cloud_file['%s/%s' % (str(id), 'core')][...],
                        cloud_file['%s/%s' % (str(id), 'core_shell')]])

    K, J, I = index_to_zyx(core_index)
    z = np.unique(K)

    GATE = '/newtera/loh/data/GATE'
    data_files = glob.glob('%s/%s/*.nc' % (GATE, 'variables'))
    data_files.sort()
    nc_file = nc(data_files[n])
    data = {'z': nc_file.variables['z'][:].astype(np.float_),
            'TABS': nc_file.variables['TABS'][:, 300:900, :].astype(np.float_),
            'QN': nc_file.variables['QN'][:, 300:900, :].astype(np.float_),
            'QI': nc_file.variables['QI'][:, 300:900, :].astype(np.float_),
            }

    mse_mean = np.zeros_like(data['z'])
    mse_stat = []
    mse_k = []
    for k in z:
        mask = (K == k)
        if mask.sum() < 2: continue

        mse_stat += list((mse(data, k, J[mask], I[mask])/1.e3).squeeze())
        mse_k += list(K[mask]*50./1.e3)

        mse_mean[k] = np.mean(mse(data, k, J[mask], I[mask]))/1.e3

    mse_mean[mse_mean == 0] = np.nan

    plt.plot(mse_mean, data['z']/1000., label='With QI')

    cmap = sns.cubehelix_palette(8, start=0.5, light=1, rot=-.75, gamma = 1.5, as_cmap=True)
    H, xi, yi = np.histogram2d(mse_stat, mse_k, bins=25, normed=False)
    plt.pcolormesh(xi, yi, np.log10(H.T)+1e-10, vmin=.1, vmax=3,  cmap=cmap, \
        alpha=.8, edgecolor='0.9', linewidths = (.2,),)
    
    plt.colorbar()

    # plt.title("Cloud core top heights")
    plt.xlabel("MSE")
    plt.ylabel("Height (km)")
    plt.legend(loc=2)

    plt.savefig('%s.png' % ('output'), bbox_inches='tight', dpi=300, \
        facecolor='w', transparent=True)

if __name__ == '__main__':
    main()
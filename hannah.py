import numpy as np
import matplotlib
matplotlib.use('Agg')

from netCDF4 import Dataset as nc
import matplotlib.pyplot as plt

import sys, glob, datetime
import h5py

import seaborn as sns

import numba
from numba import int64

import var_calcs

# @numba.jit((int64[:], int64, int64, int64), nopython=True, nogil=True)
def index_to_zyx(index, nz=320, ny=600, nx=1728):
    z = index // (ny*nx)
    index = index % (ny*nx)
    y = index // nx
    x = index % nx
    return (z, y, x)


def calc_dilution():
    dv = 50.**3
    dt = 60.

    cloudtracker = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5/'
    clouds = glob.glob("%s/clouds_*.h5" % cloudtracker)
    clouds.sort()

    GATE = '/newtera/loh/data/GATE'
    var_files = glob.glob('%s/%s/*.nc' % (GATE, 'variables'))
    var_files.sort()
    
    ent_files = glob.glob('%s/%s/*.nc' % (GATE, 'core'))
    ent_files.sort()

    cloud_file = h5py.File(clouds[60])
    ids = list(cloud_file.keys())
    
    var_file = nc(var_files[60])
    ent_file = nc(ent_files[60])

    # TODO: filter epsilon values based on core definition
    eps_var = ent_file.variables['ETETCOR'][:320, 300:900, :].astype(np.float_)

    data = {
            'ids': ids,
            'z': var_file.variables['z'][:320].astype(np.float_),
            # 'p': var_file.variables['p'][:320].astype(np.float_),
            'TABS': var_file.variables['TABS'][:320, 300:900, :].astype(np.float_),
            'QV': var_file.variables['QV'][:320, 300:900, :].astype(np.float_),
            'QN': var_file.variables['QN'][:320, 300:900, :].astype(np.float_),
            # 'QP': var_file.variables['QP'][:320, 300:900, :].astype(np.float_),       
    }

    with nc('%s/GATE_1920x1920x512_50m_1s_ent_stat.nc' % GATE) as stat_file:
        data['rho'] = stat_file.variables['RHO'][539:,:320].astype(np.float_)

    # core_points = np.hstack([cloud_file['%s/%s' % (str(id), 'core')][...],
    #                         cloud_file['%s/%s' % (str(id), 'core_shell')]])
    core_points = cloud_file['%s/%s' % (str(29904), 'core')][...]
    K, J, I = index_to_zyx(core_points)

    # thetav = var_calcs.theta_v(data['p'], data['TABS'], data['QV'], data['QN'], data['QP'])
    dil = []
    eps_list = []
    for k in np.unique(K):
        print(k)
        mask = (K == k)

        eps = eps_var[K[mask], J[mask], I[mask]] * dt

        QN = (data['QN'])[K[mask], J[mask], I[mask]] 
        QV = (data['QV'])[K[mask], J[mask], I[mask]] 
        # QP = (data['QP'])[K[mask], J[mask], I[mask]] 
        
        # QT = var_calcs.thetav(data, K[mask], J[mask], I[mask])
        QT = QN + QV

        QT = QT[(eps > 1e-6) & (eps < 10)]
        eps = eps[(eps > 1e-6) & (eps < 10)]

        def wmean(weight, b, dv):
            return (np.sum(weight * b * dv)/np.sum(weight * dv))

        var_mean = wmean(data['rho'][60, k], QT, dv)

        dil_e = (eps * dv).sum()/((data['rho'][60, k] + eps) * dv).sum() \
                * (var_mean - wmean(eps, QT, dv))/var_mean/60

        dil += [dil_e * 60]
        eps_list += [eps]


    core_data = nc('cdf/core_entrain_profile_00000060.nc')
    eps = core_data.variables['ETETCOR'][586, :]

    sha = np.zeros_like(eps)
    sha[3:3+len(dil)] = dil

    sha[np.isnan(sha)] = 0.
    eps[np.isnan(eps)] = 0.

    fig = plt.figure(1, figsize=(5, 3.125))
    fig.clf()
    ax = fig.add_subplot(111)
    

    cmap = sns.cubehelix_palette(8, start=0.5, light=1, rot=-.75, \
        gamma = 1.5, as_cmap=True)
    H, xi, yi = np.histogram2d(sha, eps, bins=35, normed=False)
    plt.pcolormesh(xi, yi, np.log10(H.T)+1e-10, vmin=.1, vmax=3,  \
        cmap=cmap, alpha=.8, edgecolor='0.9', linewidths = (.2,),)
    
    plt.colorbar()

    plt.savefig('%s.png' % ('output'), \
        bbox_inches='tight', dpi=300, facecolor='w', transparent=True)


if __name__ == '__main__':
    calc_dilution()

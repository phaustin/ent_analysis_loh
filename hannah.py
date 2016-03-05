import numpy as np

from netCDF4 import Dataset as nc
import matplotlib.pyplot as plt

import sys, glob, datetime
import h5py

import seaborn as sns

import numba
from numba import int64


# @numba.jit((int64[:], int64, int64, int64), nopython=True, nogil=True)
def index_to_zyx(index, nz=320, ny=600, nx=1728):
    z = index // (ny*nx)
    index = index % (ny*nx)
    y = index // nx
    x = index % nx
    return (z, y, x)


def calc_dilution():
    dv = 50. **3
    dt = 60.

    cloudtracker = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5/'
    clouds = glob.glob("%s/clouds_*.h5" % cloudtracker)
    clouds.sort()

    GATE = '/newtera/loh/data/GATE'
    var_files = glob.glob('%s/%s/*.nc' % (GATE, 'variables'))
    var_files.sort()
    
    ent_files = glob.glob('%s/%s/*.nc' % (GATE, 'core'))
    ent_files.sort()

    with nc('%s/GATE_1920x1920x512_50m_1s_ent_stat.nc' % GATE) as stat_file:
        rho = stat_file.variables['RHO'][539:,:320].astype(np.float_)

    cloud_file = h5py.File(clouds[60])
    ids = list(cloud_file.keys())
    id = 29875

    core_points = np.hstack([cloud_file['%s/%s' % (str(id), 'core')][...],
                            cloud_file['%s/%s' % (str(id), 'core_shell')]])

    K, J, I = index_to_zyx(core_points)
    
    var_file = nc(var_files[60])
    ent_file = nc(ent_files[60])

    QN_var = var_file.variables['QN'][:320, 300:900, :].astype(np.float_)
    QV_var = var_file.variables['QV'][:320, 300:900, :].astype(np.float_)

    # TODO: filter epsilon values based on core definition
    eps_var = ent_file.variables['ETETCOR'][:320, 300:900, :].astype(np.float_)

    dil = []
    for k in np.unique(K):
        mask = (K == k)

        QN = QN_var[K[mask], J[mask], I[mask]] / 1e3
        QV = QV_var[K[mask], J[mask], I[mask]] / 1e3
        QT = QN + QV

        eps = eps_var[K[mask], J[mask], I[mask]] * dt * dv

        dil_e = (eps.sum()/((rho[0, k] + eps).sum())) * (QT.mean() - QT.sum())/(QT.mean() * dt)
        print(eps.sum(), QT.mean())
        dil += [dil_e * (-60.)]

    print(dil)

if __name__ == '__main__':
    calc_dilution()

import numpy as np
import glob, os, sys
sys.path.append('lib/')

from netCDF4 import Dataset as nc
import h5py

if __name__ == '__main__':
    var = 'AREA'
    cloud_type = 'core'

    nc_file = nc('cdf/%s_profile_00000000.nc' % cloud_type)

    z = nc_file.variables['z'][:].astype(np.float_) / 1000.

    sns.set(rc={"figure.figsize": (4, 3)})
    plt.plot(x[1:], z)
    plt.title("Cloud core top heights")
    plt.ylabel(var)
    plt.xlabel("Altitude (km)")

    plt.savefig('png/%s.png' % ('thickness'), bbox_inches='tight', dpi=300, \
        facecolor='w', transparent=True)
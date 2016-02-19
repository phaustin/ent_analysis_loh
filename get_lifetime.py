import numpy as np
import glob, os, sys
sys.path.append('lib/')

from netCDF4 import Dataset as nc

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

    l = 0
    for item in cloud_lifetime:
        if len(cloud_lifetime[item]) > 10:
            print(item, cloud_lifetime[item])
            l += 1

    print("%d clouds" % l)
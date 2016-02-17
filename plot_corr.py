import numpy as np

from netCDF4 import Dataset as nc
import matplotlib.pyplot as plt

import sys, glob
import h5py

import seaborn as sns

def main():
    x_var = 'MSE'
    y_var = 'W'

    time_profiles = 'cdf'
    x_data = []
    y_data = []
    for n in range(10, 180, 30):
        nc_file = nc('%s/%s_profile_%08d.nc' % (time_profiles, 'core', n))
        # co_file = nc('%s/%s_profile_%08d.nc' % (time_profiles, 'core_entrain', n))

        # stat_file = nc('/newtera/loh/data/GATE/GATE_1920x1920x512_50m_1s_ent_stat.nc')
        # mean_tv = stat_file.variables['THETAV'][539+n, :320]

        # BUOY
        # x = 9.8 * (nc_file.variables['THETAV'][:].astype(np.float_) - mean_tv)/mean_tv
        x = np.log10(nc_file.variables[x_var][:].astype(np.float_) / 1.e3) # MSE
        # y = co_file.variables[y_var][:].astype(np.float_) / \
        #     co_file.variables['MFTETCOR'][:].astype(np.float_)
        y = np.log10(nc_file.variables[y_var][:].astype(np.float_))

        mask = ~(np.isnan(x) | np.isinf(x) | np.isnan(y) | np.isinf(y))
        mask = mask & (y > -1)# & (y < 0.2)

        x_data += list(x[mask])
        y_data += list(y[mask])


    fig = plt.figure(1, figsize=(6, 4))
    fig.clf()
    ax = fig.add_subplot(111)

    cmap = sns.cubehelix_palette(8, start=0.5, light=1, rot=-.75, gamma = 1.5, as_cmap=True)
    H, xi, yi = np.histogram2d(x_data, y_data, bins=25, normed=False)
    plt.pcolormesh(xi, yi, np.log10(H.T)+1e-10, vmin=.1, vmax=3,  cmap=cmap, \
        alpha=.8, edgecolor='0.9', linewidths = (.2,),)
    
    plt.colorbar()

    # Hn, _ = np.histogram(y[mask], bins=35)
    # Hy, _ = np.histogram(y[mask], bins=35, weights=x[mask])
    # Hy2, _ = np.histogram(y[mask], bins=35, weights=x[mask]**2)
    # mean = Hy / Hn
    # std = np.sqrt(Hy2/Hn - mean**2)

    # xi = (xi[1:] + xi[:-1])/2.
    # yi = (yi[1:] + yi[:-1])/2.
    # plt.plot(mean, yi, 'k-', lw=1, alpha=0.35)

    plt.title("Cloud Core Properties")
    plt.xlabel('Cloud Core %s' % x_var)
    plt.ylabel('W')

    plt.savefig('output.png', bbox_inches='tight', dpi=300, facecolor='w', transparent=True)

if __name__ == '__main__':
    main()
    

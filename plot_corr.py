import numpy as np

from netCDF4 import Dataset as nc
import matplotlib.pyplot as plt

import sys, glob, datetime
import h5py

import seaborn as sns

def plot_corr(x_var, y_var, cloud_type):
    """
    Read time_profiles data and plot the correlation between two Parameters
    in a 2D histogram

    Parameters
    ----------
    x_var: String
        Type of cloud profile (SAM statistics or entrainment variables)

    y_var: String
        Type of cloud profiles (SAM statistics or entrainment variables)

    cloud_type: String
        Type of cloud region (core, core_entrain, condensed_entrain)

    Returns
    ----------
    A 2D histogram in plots/corr_xvar_yvar.png
    """

    stat = ('AREA', 'TABS', 'QN', 'QV', 'QT', 'U', 'V', 'W', 'THETAV', \
        'THETAV_LAPSE', 'THETAL', 'MSE', 'RHO', 'PRES', 'WWREYN', 'DWDZ', 'DPDZ',)
    ent = ('DWDT', 'ETETCOR', 'DTETCOR', 'VTETCOR', 'MFTETCOR',)

    time_profiles = '/tera/users/loh/repos/ent_analysis/cdf'
    x_data = []
    y_data = []
    for n in range(10, 180, 30):
        nc_file = nc('%s/%s_profile_%08d.nc' % (time_profiles, cloud_type, n))
        co_file = nc('%s/%s_profile_%08d.nc' % (time_profiles, cloud_type, n))

        try:
            if x_var in stat:
                x = np.log10(nc_file.variables[x_var][:].astype(np.float_))
            else:
                x = np.log10(co_file.variables[x_var][:].astype(np.float_))
        except:
            print("Data not found: %s %s" % (cloud_type, x_data))
            raise

        try:
            if y_var in stat:
                y = np.log10(nc_file.variables[y_var][:].astype(np.float_))
            else:
                y = np.log10(co_file.variables[y_var][:].astype(np.float_))
        except:
            print("Data not found: %s %s" % (cloud_type, y_data))
            raise
        
        # co_file = nc('%s/%s_profile_%08d.nc' % (time_profiles, 'core_entrain', n))

        # stat_file = nc('/newtera/loh/data/GATE/GATE_1920x1920x512_50m_1s_ent_stat.nc')
        # mean_tv = stat_file.variables['THETAV'][539+n, :320]

        # BUOY
        # x = 9.8 * (nc_file.variables['THETAV'][:].astype(np.float_) - mean_tv)/mean_tv
        # x = np.log10(nc_file.variables[x_var][:].astype(np.float_) / 1.e3) # MSE
        # y = co_file.variables[y_var][:].astype(np.float_) / \
        #     co_file.variables['MFTETCOR'][:].astype(np.float_) # eps

        mask = ~(np.isnan(x) | np.isinf(x) | np.isnan(y) | np.isinf(y))

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

    plt.title("Cloud %s Correlation" % cloud_type)
    plt.xlabel('Cloud %s %s' % (cloud_type, x_var))
    plt.ylabel('Cloud %s %s' % (cloud_type, y_var))

    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    time_now = now.strftime(('%Y-%m-%d_%H:%M'))

    plt.savefig('plot/%s_corr_%s_%s.png' % (time_now, x_var, y_var), \
        bbox_inches='tight', dpi=300, facecolor='w', transparent=True)

if __name__ == '__main__':
    x_var = 'MSE'
    y_var = 'W'

    cloud_type = 'core'
    plot_corr(x_var, y_var, cloud_type)
    
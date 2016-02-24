import numpy as np

from netCDF4 import Dataset as nc
import matplotlib.pyplot as plt

import sys, glob, datetime
import h5py

import seaborn as sns

def plot_profiles_ent(var, cloud_type):
    """
    Read time_profiles_ent data and plot the vertical profiles of the 
    entrainment properties, for different types of cloud regions (core, 
    core_entrain and condensed_entrain). 

    Parameters
    ----------
    var: String
        Type of cloud profile

    cloud_type: String
        Type of cloud region (core, core_entrain, condensed_entrain)

    Returns
    ----------
    A series of plots in "plots/"

    Notes
    ----------
    For cloud core/condensed region statistics variables, see
    plot_profiles.py 
    """

    print(var)

    time_profiles = '/tera/users/loh/repos/ent_analysis/cdf'
    x_data = []
    y_data = []
    for n in range(0, 180, 5):
        # print('%s/%s_profile_%08d.nc' % (time_profiles, cloud_type, n))
        nc_file = nc('%s/%s_profile_%08d.nc' % (time_profiles, cloud_type, n))

        x = nc_file.variables[var][:].astype(np.float_)
        y = np.ones_like(x) * nc_file.variables['z'][:].astype(np.float_) / 1.e3

        mask = ~(np.isnan(x) | np.isinf(x))
        
        # Shallow filter
        if (var == 'ETETCOR') | (var == 'DTETCOR'):
            mask = mask & (x < 800)
        elif var == 'VTETCOR':
            mask = mask & (x < 100000)
        elif var == 'MFTETCOR':
            mask = mask & (x < 200000)

        x_data += [x[mask]]
        y_data += [y[mask]]

    fig = plt.figure(1, figsize=(6, 4))
    fig.clf()
    ax = fig.add_subplot(111)
    # plt.plot(x, y, lw=1)
    cmap = sns.cubehelix_palette(8, start=0.5, light=1, rot=-.75, \
        gamma = 1.5, as_cmap=True)
    H, xi, yi = np.histogram2d(x[mask], y[mask], bins=35, normed=False)
    plt.pcolormesh(xi, yi, np.log10(H.T)+1e-10, vmin=.1, vmax=3, \
        cmap=cmap, alpha=.8, edgecolor='0.9', linewidths = (.2,),)
    
    plt.colorbar()

    Hn, _ = np.histogram(y[mask], bins=35)
    Hy, _ = np.histogram(y[mask], bins=35, weights=x[mask])
    Hy2, _ = np.histogram(y[mask], bins=35, weights=x[mask]**2)
    mean = Hy / Hn
    std = np.sqrt(Hy2/Hn - mean**2)

    xi = (xi[1:] + xi[:-1])/2.
    yi = (yi[1:] + yi[:-1])/2.
    plt.plot(mean, yi, 'k-', lw=1, alpha=0.35)

    plt.title("Cloud Core %s" % var)
    plt.xlabel(var)
    plt.ylabel("Altitude (km)")

    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    time_now = now.strftime(('%Y-%m-%d_%H:%M'))

    plt.savefig('plots/%s_%s_%s.png' % (time_now, cloud_type, var.lower()), \
        bbox_inches='tight', dpi=300, facecolor='w', transparent=True)

if __name__ == '__main__':
    cloud_type = 'core_entrain'

    for var in (
        'DWDT',
        'ETETCOR',
        'DTETCOR',
        'VTETCOR',
        'MFTETCOR',
        ):

        plot_profiles_ent(var, cloud_type)
    

import numpy as np

from netCDF4 import Dataset as nc
import matplotlib.pyplot as plt

import sys, glob
import h5py

import seaborn as sns
import scipy

def main():
    x_var = 'MSE'
    y_var = 'W'

    time_profiles = 'cdf'
    x_data = []
    y_data = []
    for n in range(60, 180, 2):
        nc_file = nc('%s/%s_profile_%08d.nc' % (time_profiles, 'condensed', n))

        ids = nc_file.variables['ids'][:].astype(np.int_)

        # BUOY
        h = nc_file.variables[x_var][:, :40].astype(np.float_) / 1.e3 # MSE
        w = nc_file.variables[y_var][:, :40].astype(np.float_)

        h_reyn = np.zeros((len(ids), 40))
        w_reyn = np.zeros((len(ids), 40))
        for k in range(0, 40):
            kk = min(k+1, 40-1)

            h_k = (h[:, kk] + h[:, k])/2
            h_reyn[:, k] = (h_k**2 - np.nanmean(h_k))

            w_k = (w[:, kk] + w[:, k])/2
            w_reyn[:, k] = (w_k**2 - np.nanmean(w_k))

        #     kj = max(0, k-1)

        #     h[:, k] = (h[:, kk] - 2 * h[:, k] + h[:, kj]) / 2500.
        #     w[:, k] = (w[:, kk] - 2 * w[:, k] + w[:, kj]) / 2500.

            # k1h = min(k+1, 319)
            # k2h = min(k+2, 319)
            # h[:, k] = (h[:, k2h] - 2 * h[:, k1h]+ h[:, k]) / 2500.
            # w[:, k] = (w[:, k2h] - 2 * w[:, k1h]+ w[:, k]) / 2500.

        x = np.log10(np.diff(h, n=1))
        y = np.log10(np.diff(w, n=1))
        # x = np.diff(h, n=1)
        # y = np.diff(w, n=1)
        # x = np.log10(h)
        # y = np.log10(w)
        # x = h_reyn
        # y = w_reyn

        mask = ~(np.isnan(x) | np.isinf(x) | np.isnan(y) | np.isinf(y))
        # mask = mask & (x > -8) & (y > -8)
        # mask = mask & (np.abs(y) < 1) & (np.abs(x) < 1)

        x_data += list(x[mask])
        y_data += list(y[mask])

    fig = plt.figure(1, figsize=(6, 4))
    fig.clf()
    ax = fig.add_subplot(111)

    print(np.corrcoef(x_data, y_data))

    cmap = sns.cubehelix_palette(8, start=0.5, light=1, rot=-.75, gamma = 1.5, as_cmap=True)
    H, xi, yi = np.histogram2d(x_data, y_data, bins=25, normed=False)
    plt.pcolormesh(xi, yi, np.log10(H.T)+1e-10, vmin=.1, vmax=3,  cmap=cmap, \
        alpha=.8, edgecolor='0.9', linewidths = (.2,),)
    
    plt.colorbar()

    # Hn, _ = np.histogram(y[mask], bins=25)
    # Hy, _ = np.histogram(y[mask], bins=25, weights=x[mask])
    # Hy2, _ = np.histogram(y[mask], bins=25, weights=x[mask]**2)
    # mean = Hy / Hn
    # std = np.sqrt(Hy2/Hn - mean**2)

    # xi = (xi[1:] + xi[:-1])/2.
    # yi = (yi[1:] + yi[:-1])/2.
    # plt.plot(mean, yi, 'k-', lw=1, alpha=0.35)

    # plt.title("Cloud Core Properties")
    plt.xlabel('h\"')
    plt.ylabel('W\"')

    plt.savefig('output.png', bbox_inches='tight', dpi=300, facecolor='w', transparent=True)

if __name__ == '__main__':
    main()
    

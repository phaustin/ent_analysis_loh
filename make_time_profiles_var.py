import numpy as np
import sys, glob

from netCDF4 import Dataset as nc
import h5py, time

import var_calcs

GATE = '/newtera/loh/data/GATE'
HDF5 = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5'

def make_profile(z_indexes, y_indexes, x_indexes,
                 data, variables, profiles):

    z = np.unique(z_indexes)
    for k in z:
        mask = (z_indexes == k)
        if mask.sum() == 0: continue
        j = y_indexes[mask]
        i = x_indexes[mask]
        for name in variables:
            profiles[name][k] = variables[name](data, k, j, i)

    return profiles


def index_to_zyx(index):
    ny, nx = 600, 1728
    z = index // (ny*nx)
    index = index % (ny*nx)
    y = index // nx
    x = index % nx
    return np.array((z, y, x))


def make_profiles(profiles, cloud_data, var_list, data, n):
    for item in ('core', 'condensed'):
        variables = profiles[item]
                
        temp_profile = {}
        for name in var_list:
            temp_profile[name] = np.ones_like(data['z'][:])*np.NaN

        indexes = cloud_data[item]
        if len(indexes) > 0:
            z, y, x = index_to_zyx(indexes)            
            results = make_profile(z, y, x, data, var_list, temp_profile)
        else:
            results = temp_profile       
                                               
        for name in var_list:
            variables[name][n, :] = results[name]


def create_savefile(t, data, variables, profile_name):
    ids = data['ids'][:]
    z = data['z'][:]
    # print 'cdf/%s_profile_%08d.nc' % (profile_name, t)
    savefile = nc('cdf/%s_profile_%08d.nc' % (profile_name, t), 'w', format='NETCDF4')
    
    # Create savefile
    savefile.createDimension('ids', len(ids))
    savefile.createDimension('z', len(z))

    tsavevar = savefile.createVariable('ids', 'd', ('ids',))
    tsavevar[:] = ids[:]
    zsavevar = savefile.createVariable('z', 'd', ('z',))
    zsavevar[:] = z[:]

    vars = {}
    for name in variables:
        vars[name] = savefile.createVariable(name, 'd', ('ids', 'z'))
        
    return savefile, vars


def main(clouds):
    """
    Read the output from the cloud-tracking algorithm and process the SAM
    output variables for each individual cloud at every model altitude, or
    in (ids, height). 

    Parameters
    ----------
    clouds: list of string
        List of cloudtracker output: clouds_%08d.py

    Returns
    ----------
    Times profiles in ./cdf/ for each type of region (core, core_shell, etc)

    Notes
    ----------
    Currently, _edge and _env processing is turned off in cloudtracker
    """

    variables = {
          'AREA': var_calcs.area,
          'TABS': var_calcs.tabs,
          'QN': var_calcs.qn,
          'QV': var_calcs.qv,
          'QT': var_calcs.qt,
          'U': var_calcs.u,
          'V': var_calcs.v,
          'W': var_calcs.w,
          'THETAV': var_calcs.thetav,
          'THETAV_LAPSE': var_calcs.thetav_lapse,
          'THETAL': var_calcs.thetal,
          'MSE': var_calcs.mse,
          'RHO': var_calcs.rho,
          'PRES': var_calcs.press,
          # 'WQREYN': var_calcs.wqreyn,
          'WWREYN': var_calcs.wwreyn,
          'DWDZ': var_calcs.dw_dz,
          'DPDZ': var_calcs.dp_dz,
          # 'TR01': var_calcs.tr01, # NOTE: do not use tracers
    }

    # cloud_types = ('condensed', 'condensed_shell', 
    #              'condensed_edge', 'condensed_env',
    #              'core', 'core_shell', 
    #              'core_edge', 'core_env', 'plume')
    cloud_types = ('core', 'core_shell', 'condensed', 'condensed_shell')

    with nc('%s/GATE_1920x1920x512_50m_1s_ent_stat.nc' % GATE) as stat_file:
        rho = stat_file.variables['RHO'][539:,:320].astype(np.float_)

    data_files = glob.glob('%s/%s/*.nc' % (GATE, 'variables'))
    data_files.sort()

    for n, cloud in enumerate(clouds):
        cloud_file = h5py.File('%s/clouds_%08d.h5' % (HDF5, n))
        ids = list(cloud_file.keys())
        ids.sort()

        print(data_files[n])
        nc_file = nc(data_files[n])

        data = {'z': nc_file.variables['z'][:].astype(np.float_),
            'p': nc_file.variables['p'][:].astype(np.float_),
            'RHO' : rho[n, :], 'ids': np.array(ids),
            }

        for name in  ('QV', 'QN', 'QI', 'TABS', 'PP', 'U', 'V', 'W'):
            # Note: Be careful when handling sub-domain
            print('\t Reading...%s                            ' % name, end='\r')
            data[name] = nc_file.variables[name][:, 300:900, :].astype(np.float_)

        # For each cloud, create a savefile for each profile
        savefiles = {}
        profiles = {}
        for item in cloud_types:
            savefile, var = create_savefile(n, data, variables, item)
            profiles[item] = var
            
        cloud = {}
        for n, id in enumerate(ids):
            # print "time: ", time, " id: ", id
            # Select the current cloud id
            #cloud = clouds[id]
            for item in cloud_types:
              cloud[item] = cloud_file['%s/%s' % (str(id), item)][...]

            make_profiles(profiles, cloud, variables, data, n)

        nc_file.close()
        for savefile in savefiles.values():
            savefile.close()

    print('')

if __name__ == '__main__':
    cloudtracker = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5/'
    clouds = glob.glob("%s/clouds_*.h5" % cloudtracker)
    clouds.sort()

    main(clouds) # First 60 minutes
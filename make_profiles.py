import numpy as np
import sys, glob

from netCDF4 import Dataset as nc
import h5py, time

import var_calcs

GATE = '/newtera/loh/data/GATE'
HDF5 = '/tera/users/loh/repos/ent_analysis/hdf5'

y1 = 300 ; y2 = 900

def make_profile(z_indexes, y_indexes, x_indexes,
                 data, variables, profiles):

    z = numpy.unique(z_indexes)
    for k in z:
        mask = (z_indexes == k)
        if mask.sum() == 0: continue
        j = y_indexes[mask]
        i = x_indexes[mask]
        for name in variables:
            profiles[name][k] = variables[name](data, k, j, i)

    return profiles


def index_to_zyx(index):
    ny, nx = mc.ny, mc.nx
    z = index // (ny*nx)
    index = index % (ny*nx)
    y = index // nx
    x = index % nx
    return numpy.array((z, y, x))


def make_profiles(profiles, cloud_data, variables, data, n):
    for item in ('condensed', 'condensed_shell', 
                 'condensed_edge', 'condensed_env',
                 'core', 'core_shell', 
                 'core_edge', 'core_env', 'plume'):
        variables = profiles[item]
                
        temp_profile = {}
        for name in variables:
            temp_profile[name] = ones_like(data['z'][:])*numpy.NaN

        indexes = cloud_data[item]
        if len(indexes) > 0:
            z, y, x = index_to_zyx(indexes)            
            results = make_profile(z, y, x,
                                   data, variables, temp_profile)
        else:
            results = temp_profile       
                                               
        for name in variables:
            variables[name][n, :] = results[name]


def create_savefile(t, data, variables, profile_name):
    ids = data['ids'][:]
    z = data['z'][:]
    # print 'cdf/%s_profile_%08d.nc' % (profile_name, t)
    savefile = Dataset('cdf/%s_profile_%08d.nc' % (profile_name, t), 'w', format='NETCDF4')
    
    # Create savefile
    savefile.createDimension('ids', len(ids))
    savefile.createDimension('z', len(z))

    tsavevar = savefile.createVariable('ids', 'd', ('ids',))
    tsavevar[:] = ids[:]
    zsavevar = savefile.createVariable('z', 'd', ('z',))
    zsavevar[:] = z[:]

    variables = {}
    for name in variables:
        variables[name] = savefile.createVariable(name, 'd', ('ids', 'z'))
        
    return savefile, variables


def main(clouds):
    variables = {
          'AREA': var_calcs.area,
          'TABS': var_calcs.tabs,
          # 'QN': var_calcs.qn,
          'QV': var_calcs.qv,
          'QT': var_calcs.qt,
          # 'U': var_calcs.u,
          # 'V': var_calcs.v,
          'W': var_calcs.w,
          'THETAV': var_calcs.thetav,
          'THETAV_LAPSE': var_calcs.thetav_lapse,
          # 'THETAL': var_calcs.thetal,
          'MSE': var_calcs.mse,
          'RHO': var_calcs.rho,
          'PRES': var_calcs.press,
          # 'WQREYN': var_calcs.wqreyn,
          'WWREYN': var_calcs.wwreyn,
          'DWDZ': var_calcs.dw_dz,
          # 'DPDZ': var_calcs.dp_dz,
          # 'TR01': var_calcs.tr01, # NOTE: do not use tracers
    }

    core = {
          'DWDT': var_calcs.dwdt,
          'ETETCOR': var_calcs.etetcor,
          'DTETCOR': var_calcs.dtetcor,
          # 'EQTETCOR': var_calcs.eqtetcor,
          # 'DQTETCOR': var_calcs.dqtetcor,
          # 'ETTETCOR': var_calcs.ettetcor,
          # 'DTTETCOR': var_calcs.dttetcor,
          # 'EWTETCOR': var_calcs.ewtetcor,
          # 'DWTETCOR': var_calcs.dwtetcor,
          # 'VTETCOR': var_calcs.vtetcor,
          'MFTETCOR': var_calcs.mftetcor,
    }

    condensed = {
          'ETETCLD': var_calcs.etetcld,
          'DTETCLD': var_calcs.dtetcld,
          # 'EQTETCLD': var_calcs.eqtetcld,
          # 'DQTETCLD': var_calcs.dqtetcld,
          # 'ETTETCLD': var_calcs.ettetcld,
          # 'DTTETCLD': var_calcs.dttetcld,
          # 'EWTETCLD': var_calcs.ewtetcld,
          # 'DWTETCLD': var_calcs.dwtetcld,
          # 'VTETCLD': var_calcs.vtetcld,
          'MFTETCLD': var_calcs.mftetcld,
    }

    # cloud_types = ('condensed', 'condensed_shell', 
    #              'condensed_edge', 'condensed_env',
    #              'core', 'core_shell', 
    #              'core_edge', 'core_env', 'plume')
    cloud_types = ('core', 'condensed')

    with nc('%s/GATE_1920x1920x512_50m_1s_ent_stat.nc' % GATE) as stat_file:
        rho = stat_file.variables['RHO'][540:,:320].astype(np.float_)

    data_files = glob.glob('%s/%s/*.nc' % (GATE, 'variables'))
    data_files.sort()

    for n, cloud in enumerate(clouds):
        cloud_file = h5py.File('hdf5/clouds_%08d.h5' % n)
        ids = list(cloud_file.keys())
        ids.sort()

        print(data_files[n])
        nc_file = nc(data_files[n])

        data = {'z': nc_file.variables['z'][:, y1:y2, :].astype(np.float_),
            'p': nc_file.variables['p'][:, y1:y2, :].astype(np.float_),
            'RHO' : rho[n, :], 'ids': np.array(ids),
            }

        for name in ('QV', 'TABS', 'PP', 'W'):
            data[name] = nc_file.variables[name][:, y1:y2].astype(np.np.float_)

        # For each cloud, create a savefile for each profile
        savefiles = {}
        profiles = {}
        for item in cloud_types:
            savefile, variables = create_savefile(time, data, variables, item)
            savefiles[item] = savefile
            profiles[item] = variables
            
        cloud = {}
        for n, id in enumerate(ids):
            # print "time: ", time, " id: ", id
            # Select the current cloud id
            #cloud = clouds[id]
            for item in cloud_types:
              cloud[item] = cloud_file['%s/%s' % (str(id), item)][...]

            make_profiles(profiles, cloud, variables, data, n)
    print('')

if __name__ == '__main__':
    cloudtracker = '/newtera/loh/workspace/cloudtracker/cloudtracker/hdf5/'
    clouds = glob.glob("%s/clouds_*.h5" % cloudtracker)
    clouds.sort()

    main(clouds[:2]) # First 30 minutes
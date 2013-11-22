[ent_analysis](https://github.com/lorenghoh/ent_analysis "ent_analysis")
==========

## Entrainment analysis toolkit for SAM ##
The **entrainment analysis toolkit** is a package used to post-process output data generated by SAM ([System for Atmospheric Modelling](http://rossby.msrc.sunysb.edu/~marat/SAM.html)) with entrainment calculation implemented by Dawe and Austin (2011a). This package combines (parallelized and automated) SAM output conversion (```bin3D2nc```), cloudtracker and several different post-process scripts. 

 The raw ```.bin3D``` data from SAM is converted, and sorted to be used by  [*cloudtracker*](https://github.com/freedryk/cloudtracker). Then for each cloud parcel, the package creates a ```netCDF``` file containing all the relevant output data from SAM. Now with the individual cloud data collected by ```cloudtracker```, it is possible to apply reanalysis scripts (or *analysis modules*) to produce a more detailed picture of each cloud parcel -- these *modules* will modify output ```netCDF``` files and add additional statistical variables needed for the entrainment analysis. 

## Current status ##
```ent_analysis``` is now in production. 

### In Progress ###
- [ ] Output control
- [ ] Check file creation to avoid duplicates

### Next ###
- [ ] Automatically read dimensions from input files
- [ ] Ensure no data contamination by re-run

### Maybe ###
- [ ] Parallelize [*cloudtracker*](https://github.com/freedryk/cloudtracker) module 

## Getting Started ##
 To run the entrainment analysis toolkit, the following Python modules **must** be installed (as needed for the [*cloudtracker*](https://github.com/freedryk/cloudtracker) module):

- numpy
- networkx
- netcdf4-python *or* pupynere

### Installation ###
Download ent_analysis package to SAM directory, or where the model output will be stored for better performance (*recommended* if the storage is limited, as the entrainment analysis package will also store the processed data). Ensure that the configuration file ```config.cfg``` is properly modified according to the system configuration. 

### Example ###
 To run entrainment analysis toolkit, simple run:```./run_analysis.py```

Or, use the MOAB script ```msub MOAB```

### Output ###
```id_profiles``` module is turned off by default. Hence, locate the output data files at ```/time_profiles/cdf```.
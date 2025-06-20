* CESM1 case directory for a geoengineering run
This folder contains all settings that were used to run the CESM1 with feedback controller.

Help for installing CESM and making changes for geoengineering scenarios can be found at our [wiki](https://github.com/UU-IMAU/cesm-srm/wiki).  

To save disk space, the feedback controller code has been removed from the case directory. To use it, copy the `CESM1` folder in `controller` in the case directory and rename it to `controller`. The feedback controller is called in `Tools/ccsm_postrun.csh`.


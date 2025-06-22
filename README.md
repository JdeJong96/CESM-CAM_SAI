# CESM-CAM_SAI
Source code and (to be) published results for forcing our geoengineering simulations with CESM-CAM.

This project contains scripts we developed to force global geoengineering simulations with CESM-CAM using the emulation method described in the technical paper. It is divided into three parts:

1) preprocess
     analysis of pre-existing geoengineering simulation with proper stratospheric chemistry to fit relations of stratospheric fields with changes in aerosol optical depth (or any other key metric)
2) controller
     source code to regulate forcing in CESM-CAM (runs offline after each full model year)
3) results
     data and source code for published figures in [SAI_in_CAM paper]

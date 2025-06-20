# Code suite for the feedforward-feedback controller
Scripts used to prescribe stratospheric aerosols in CESM1-CAM5 based on CESM-WACCM output. Used at [IMAU](https://www.uu.nl/onderzoek/imau) to perform simulations of feedback-controlled stratospheric aerosol injection. Contributors: Daniel Pflüger, Leo van Kampenhout, Jasper de Jong, Claudia Wieners

The controller component was originally built by [Ben Kravitz](https://github.com/bkravitz/feedback_suite) and updated by Daniele Visioni. See [Kravitz et al. (2016), _Earth System Dynamics_](https://esd.copernicus.org/articles/7/469/2016/) for more context.

## Input
* `exp_fields_jasper_01`, `fit_params_jasper_01`: netcdfs of averaged fields and fit parameters for AOD->amplitude conversion  
These input fields and conversion relations need to be derived from a pre-existing dataset. For this, see the `preprocess` folder.
Here, we used [WACCM data](https://doi.org/10.5065/D6JH3JXX) from the GLENS project.


## Feedforward-feedback controller:
* `main.py`, `driver.py`, `commonroutines.py`: utilities for running the controller and coupling it to CESM2, written by Ben Kravitz with minor modifications from our side
* `PIcontrol_exp_fields.py`: controller for SAI 2020/2050, adapted from Ben Kravitz' original script
* `PIcontrol_exp_fields_orig.py`: controller (Ben Kravitz' original script)


## Generate forcing
* `expected_fields.py`, `geo_tools.py`, `norm_const_fit.py`: scale the aerosol forcing field
* `adjustvolcaeroforcing.py`: convert to volcanic aerosol and write forcing file
* `strataero_forcing.py`: update MAM4 stratospheric forcing file (same variables as WACCM)

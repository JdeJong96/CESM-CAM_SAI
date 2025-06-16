# Explicit feedback code suite
# Sample control parameters file
#
# Written by Ben Kravitz (ben.kravitz@pnnl.gov or ben.kravitz.work@gmail.com)
# Last updated 29 November 2016 -> note D.P.: see comment below
#
# This script provides information about the feedback algorithm.  All of this
# is user-customizable.  The other parts of the script will give you outvals,
# lats, lons, and times.  The output of this script should be a list called
# nlvals, which consists of pairs.  The first item in the pair is the name
# of the namelist value.  The second item is the value itself as a string.
#
# This script is written in native python format.  Be careful with brackets [],
# white space, and making sure everything that needs to be a string is actually
# a string by putting it in quotes ''.  All lines beginning with # are comments.

#
# Modified by Daniel Pflueger, Claudia Wieners and Leo Kampenhout on 2021-10-01
# for use in IMAU CESM-CAM 6 SAI in RCP 8.5 scenario with PI+1.5 degC target run
# Contacts: d.pfluger@uu.nl, C.E.Wieners@uu.nl, l.vankampenhout@uu.nl
#

#
# Comment 2022-02-24: This version of the feedback controller dynamically introduces the integrator depending on two conditions:
# The temperature error terms are summed after...
# - the temperature error is within a defined distance of the reference temperature
# OR
# - a defined amount of years have past since the initialization of the controller
# After any of these conditions is met, the integrator remains switched on indefinitely
#
# Update 2022-12-01 by Jasper de Jong: By setting USE_INTEGRATOR_RESET to True, 
# instead of the above, the feedback controller will always calculate and apply
# the intyegrator term, but reset the sum(dT0) to zero once the target temperature
# has been reached for the first time. 

#
# TO-DO's:
# - extend forcing beyond 2100 (which CO2 scenario? looping control fields?)
#

from __future__ import print_function
import os
import strataero_forcing
import adjustvolcaeroforcing as avf
import norm_const_fit as nc
import xarray as xr

#### IMPORTANT FILE PATHS ####

#fit_consts_path = './nc_from_aod_params/' # path to fit parameters used by nc.all_norms_from_main_field
#exp_fields_path = './exp_field_simple_avg_data/' # path to exp fields used by strataero_forcing.load_exp_fields

fit_consts_path = os.path.join(maindir,'fit_params_jasper_01/') # path to fit parameters used by nc.all_norms_from_main_field
exp_fields_path = os.path.join(maindir,'exp_fields_jasper_01/') # path to exp fields used by strataero_forcing.load_exp_fields
#fit_consts_path = os.path.join(maindir,'fit_params_test/') # path to fit parameters used by nc.all_norms_from_main_field
#exp_fields_path = os.path.join(maindir,'exp_fields_test/') # path to exp fields used by strataero_forcing.load_exp_fields
#print('WARNING: USING TEST FILES NOT CORRECT FIELDS')

# strataero file
# this is the CURRENT FILE, i.e. that is continuously updated
# and referenced in the user namelist: user_nl_cam

#prescribed_strataero_datapath          = '/projects/0/uuesm/GeoEng/feedback/'
prescribed_strataero_datapath           = f'/projects/0/nwo2021025/archive/{casename}/strataero'
prescribed_strataero_file               = "ozone_strataero_2019-2100_SSP585_CAMfeedback.nc"

if (not os.path.exists(prescribed_strataero_datapath)):
    print('INFO: creating '+prescribed_strataero_datapath)
    os.makedirs(prescribed_strataero_datapath)
    assert(os.path.exists(prescribed_strataero_datapath))

strataero_path_namelist = os.path.join(prescribed_strataero_datapath ,prescribed_strataero_file)

# This is the original strataero, only needed once (at the start)
strataero_path_cnt = '/projects/0/nwo2021025/feedback_LR/ozone_strataero1mode_blanked.nc'

#### PREPARE LOG ####

logfilename='ControlLog_'+casename+'.txt'

logheader=['Timestamp','dT0','sum(dT0)','L0','L0hat','int_weight','n_AODVISstdn',
           'n_H2SO4_mass','n_rmode','n_sad',
           'n_H2SO4_mmr','n_SAD_AERO','REFF_AERO']

           #'n_so4mass_a1','n_so4mass_a2','n_so4mass_a3',
           #'n_diamwet_a1','n_diamwet_a2','n_diamwet_a3',
           #'n_SAD_AERO']

# 'firsttime' is a flag value that is set to 1 if the script is run for the first time
# in this first run, an output log is created
firsttime=0
if os.path.exists(maindir+'/'+logfilename)==False: # where is maindir defined?
    firsttime=1
    print('INFO: first time')
else:
    loglines=readlog(maindir+'/'+logfilename)
    print('INFO: continuation')




BLAAAAAAAAAAAAAAAAAA







#### USER-SPECIFIED CONTROL PARAMETERS ####

refvals=[287.46] # temperature in 2051 = 289.28221851042696

# --- meeting 12 Oct 2022, new targets
#refvals=[287.46] # LR target HighResMIP
#refvals=[289.17] # HR target HighResMIP
# ---

kivals=[0.028] # integration parameter of feedback "k_i"
kpvals=[0.028] # proportional parameter of feedback "k_p"
firstyear=2000 # starting year of feedback
baseyear=2015  # only to define the dt for computing the feedforward. keep at 2020 when re-using the WACCM feedforward.
kff = 0.004264# feedforward constant
# Integrator ramp-up: summation of error terms is ramped up over a time interval
# This is achieved by multiplying error terms with a weight factor from 0 to 1 that is linearly raised over a given time interval
int_onset_threshold = 0.5 # Temperature deviation threshold for onset of integrator
int_failsafe_time = 6 # Time interval after which to start integrator in case other onset condition is not met
#+++JDJ+++
USE_INTEGRATOR_RESET = True  # bool, if True: int_weight=1, sum(dT0) gets reset to zero once upon reaching target temp
#+++JDJ+++

# correct the feedforward term used by Tilmes et. al.
# our control run gives 5.5K/century warming,
# in the geoengineering run (using the WACCM forcing as provided by Tilmes et. al.) leaves a 1.3K/century residual warming
# the following correction factor incorporates this fact
#CAM_WACCM_corrfac = 5.5/(5.5-1.3)





#### IMPORTANT FILE PATHS ####

#
# 2021-10-01
#
# Extract previous timestamp from log (or initialize if this is the first time)
if firsttime==1:          #the sum over all previous errors (integral term)
    timestamp=firstyear
else:
    timestamp=int(loglines[-1][0])+1

# To prevent mistakes when reading the log file (e.g. indexation errors), test the obtained timestamp
assert timestamp>1900 and timestamp<2300, 'Unrealistic timestamp from previous year. Are you reading the log file correctly?'
print(f'INFO: year = {timestamp}')





#### FEEDBACK COMPUTATION ####

# compute the temperature goals (in our case, only T0 which is global mean surface temp.) and error terms

#w=makeweights(lats,lons) # LvK: hack for Spectral Element data
#T0=numpy.mean(gmean(outvals[0],w)) # LvK: hack for Spectral Element data
assert(len(da_var) == 12) # LvK 12 months
TREFHT_mean = da_var.mean(dim='time')
T0 = (1/da_area.sum() * TREFHT_mean*da_area).sum(dim='ncol').item()

print('DEBUG T0',T0)
#sys.exit(0)

de=numpy.array([T0-refvals[0]]) # error terms: last years' deviation from the goal

int_weight = 0 # Integrator weight is binary: 0 or 1

if not firsttime==1: # Once integrator has been activated, always leave it on / Can only be executed if log file already exists, hence 'not firsttime' is required
    previous_int_weight = int(loglines[-1][4])
    # Check that previous int_weight was read correctly
    assert previous_int_weight==0 or previous_int_weight==1, 'Non-binary int weight from previous year. Are you reading the log file correctly?'
    if previous_int_weight==1:
        int_weight = 1
if abs(de)<int_onset_threshold: # Activate integrator once temperature error is within acceptable range
    int_weight = 1
if timestamp >= (firstyear + int_failsafe_time): # Activate integrator after defined time period has passed
    int_weight = 1
#+++JDJ+++
if USE_INTEGRATOR_RESET:
    int_weight = 1 # Integrator is always active
    if not firsttime==1:
        de_history = numpy.array([line[1] for line in loglines[1:]], dtype=float) # all logged temperature error 
        integrator_has_reset = any(de_history<0)  # make sure we only reset the first time when de < 0
#+++JDJ+++

if firsttime==1:          # Computing sum of error terms for integrator. This includes the binary weight factor int_weight
    sumde=de*int_weight
    #+++JDJ+++
    if USE_INTEGRATOR_RESET:
        assert(de[0]>=0, f'Cannot reset integrator because dT0 < 0 in first year ({timestamp})')
    #+++JDJ+++
else:
    sumdt0=float(loglines[-1][2])+(T0-refvals[0])*int_weight # include weight factor for error sum/this is in implementation of the integrator ramp-up
    sumde=numpy.array([sumdt0])
    #+++JDJ+++
    if USE_INTEGRATOR_RESET and (not integrator_has_reset) and (de[0] < 0):
        print(f'INFO [{timestamp}]: de = {de[0]:0.3f} - resetting sum(dT0) = {sumde[0]:0.3f} to 0.')
        sumde[0] = 0 # prevent overcooling after reaching target due to the integrated error
    #+++JDJ+++

dt = timestamp - baseyear


#first, we compute the feedforward and feedback, hence the total "geoengineering strength", in terms of AOD patterns (only l0 in our case)

# feedforward
# based on the WACCM simulation, but scaled with CAM_WACCM_corrfac to take into account that CAM needs more cooling.
#l0hat=0.0079*dt * CAM_WACCM_corrfac
l0hat = kff * dt

# feedback
l0kp1=kpvals[0]*de[0]+kivals[0]*sumde[0]

# all of the feeds
l0step4=l0kp1+l0hat

l0=max(l0step4,0)
ell=numpy.array([[l0]])


### UPDATING FORCING FILE ###


if (firsttime):
    print(f'INFO: base file: {strataero_path_cnt}')
    strataero_old = strataero_path_cnt
else:
    strataero_old = os.path.join(prescribed_strataero_datapath, prescribed_strataero_prevyear )

assert os.path.isfile(strataero_old), f'file not found: {strataero_old}'

strataero_path = os.path.join(prescribed_strataero_datapath, prescribed_strataero_curyear) 


print(f'INFO: storing result in {prescribed_strataero_curyear}')

# Load expected fields
exp_fields = strataero_forcing.load_expected_fields(exp_fields_path )

with xr.open_dataset(strataero_old) as strataero_ds:

    aod_norm = l0 # this includes Claudia's correction factor
    #
    # add ramp up in here. sth like aod_rampup = ramp_up(aod_norm,timestamp)
    # where ramp_up is a function that linearly interpolates between 0 and aod_norm
    # from the initial year to the target year
    #
    norm_consts = nc.all_norms_from_main_field(aod_norm,fit_consts_path)
    norm_consts['AODVISstdn'] = aod_norm

    print('INFO: calling strataero_forcing.update_strataero()')
    strataero_forcing.update_strataero(strataero_ds,timestamp,norm_consts,exp_fields) # IN-PLACE update of strataero_ds
    print('INFO: leaving strataero_forcing.update_strataero()')

    #
    # TO-DO Leo: is it possible to simply overwrite the current forcing file?
    # if not, do you think we should just write a new one and reference that one in the future?
    # 2021-10-01
    #

    # Note LvK: need to write NetCDF3, as NetCDF4 does seem to give errors within CESM
    strataero_ds.to_netcdf(strataero_path, format='NETCDF3_64BIT')


#strataero_ds.to_netcdf('foo.nc')

#
# TO-DO Leo: can you please change the 'nlvals = ...' declaration? This probably feeds the updated forcing file to CESM, right?
# 2021-10-01
#


prescribed_strataero_file = os.path.basename(strataero_path)
nlname1 = 'prescribed_strataero_file' 
nlval1 = f"prescribed_strataero_file = '{prescribed_strataero_file}'"
print(nlval1)

nlvals = [nlname1,nlval1] 

#### WRITE LOG ####

newline = [str(timestamp),str(de[0]),str(sumde[0]),str(l0),str(int_weight),
           str(norm_consts['AODVISstdn']),
           str(norm_consts['H2SO4_mass']), str(norm_consts['rmode']), str(norm_consts['sad']), 
           str(norm_consts['H2SO4_mmr']), str(norm_consts['SAD_AERO']), str(norm_consts['REFF_AERO']) ]

         #  str(norm_consts['so4mass_a1']),str(norm_consts['so4mass_a2']),str(norm_consts['so4mass_a3']),
         #  str(norm_consts['diamwet_a1']),str(norm_consts['diamwet_a2']),str(norm_consts['diamwet_a3']),
         #  str(norm_consts['SAD_AERO'])]

if firsttime==1:
    linestowrite=[logheader,newline]
else:
    linestowrite=[]
    for k in range(len(loglines)):
        linestowrite.append(loglines[k])
    linestowrite.append(newline)

writelog(maindir+'/'+logfilename,linestowrite)

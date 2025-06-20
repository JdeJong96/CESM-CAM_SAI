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
# TO-DO's:
# - extend forcing beyond 2100 (which CO2 scenario? looping control fields?)
# - adding ramp-up of feedback
#

from __future__ import print_function
import os
import strataero_forcing
import norm_const_fit as nc
import xarray as xr

#### IMPORTANT FILE PATHS ####

#
# TO-DO Leo: can you enter the path to the strataero forcing file in 'strataero_path'?
# 2021-10-01
#

fit_consts_path = './nc_from_aod_params/' # path to fit parameters used by nc.all_norms_from_main_field
exp_fields_path = './exp_field_simple_avg_data/' # path to exp fields used by strataero_forcing.load_exp_fields

# This is the strataero file that is continuously updated

# LvK: identical to user_nl_cam
prescribed_strataero_datapath		= '/projects/0/uuesm/GeoEng/feedback/'
prescribed_strataero_file		= 'ozone_strataero_WACCM_L70_zm5day_2015-2100_SSP585_CAMfeedback.nc'

strataero_path = os.path.join(prescribed_strataero_datapath ,prescribed_strataero_file)	
print(strataero_path)
        

# This is the original strataero, 
strataero_path_cnt = '/projects/0/uuesm/inputdata/atm/cam/ozone_strataero/ozone_strataero_WACCM_L70_zm5day_2015-2100_SSP585_c190529.nc'


#### PREPARE LOG ####

logfilename='ControlLog_'+runname+'.txt'

logheader=['Timestamp','dT0','sum(dT0)','L0',
           'n_AODVISstdn',
           'n_so4mass_a1','n_so4mass_a2','n_so4mass_a3',
           'n_diamwet_a1','n_dwea2','n_dwea3',
           'n_SADae']

# 'firsttime' is a flag value that is set to 1 if the script is run for the first time
# in this first run, an output log is created
firsttime=0
if os.path.exists(maindir+'/'+logfilename)==False: # where is maindir defined?
    firsttime=1
    print('INFO: First time')
else:
    loglines=readlog(maindir+'/'+logfilename)
    print('INFO: continuation')


#### USER-SPECIFIED CONTROL PARAMETERS ####

refvals=[288.73] # 288.78 would be 1.5 deg above the last 100yr of PI of CESM2-CAM CMIP6 database: change? \TODO
kivals=[0.028] # integration parameter of feedback "k_i"
kpvals=[0.028] # proportional parameter of feedback "k_p"
firstyear=2080 # starting year of feedback
baseyear=2020  # only to define the dt for computing the feedforward. keep at 2020 when re-using the WACCM feedforward.

# correct the feedforward term used by Tilmes et. al.
# our control run gives 5.5K/century warming,
# in the geoengineering run (using the WACCM forcing as provided by Tilmes et. al.) leaves a 1.3K/century residual warming
# the following correction factor incorporates this fact
CAM_WACCM_corrfac = 5.5/(5.5-1.3)

#
# TO-DO Claudia: not really a 'to-do' but could you explain again why we need this factor? I'll keep it for now in the code below
# 2021-10-01
#
trans_l0_AOD = 1.1 #Daniel gets somewhat higher actual AOD L0 patterns than the WACCM logfiles get as desired L0 in feedback

#### FEEDBACK COMPUTATION ####

# compute the temperature goals (in our case, only T0 which is global mean surface temp.) and error terms

w=makeweights(lats,lons)
T0=numpy.mean(gmean(outvals[0],w))
de=numpy.array([T0-refvals[0]]) # error terms: last years' deviation from the goal

if firsttime==1:          #the sum over all previous errors (integral term)
    timestamp=firstyear
    sumde=de

else:
    timestamp=int(loglines[-1][0])+1
    sumdt0=float(loglines[-1][2])+(T0-refvals[0])
    sumde=numpy.array([sumdt0])

dt = timestamp - baseyear


#first, we compute the feedforward and feedback, hence the total "geoengineering strength", in terms of AOD patterns (only l0 in our case)

# feedforward
# based on the WACCM simulation, but scaled with CAM_WACCM_corrfac to take into account that CAM needs more cooling.
l0hat=0.0079*dt * CAM_WACCM_corrfac

# feedback
l0kp1=kpvals[0]*de[0]+kivals[0]*sumde[0]

# all of the feeds
l0step4=l0kp1+l0hat

l0=max(l0step4,0)
ell=numpy.array([[l0]])


### UPDATING FORCING FILE ###

# Load expected fields 
exp_fields = strataero_forcing.load_expected_fields(exp_fields_path )

with xr.open_dataset(strataero_path_cnt) as strataero_ds:

    aod_norm = l0 * trans_l0_AOD # this includes Claudia's correction factor
    #
    # add ramp up in here. sth like aod_rampup = ramp_up(aod_norm,timestamp)
    # where ramp_up is a function that linearly interpolates between 0 and aod_norm
    # from the initial year to the target year
    #
    norm_consts = nc.all_norms_from_main_field(aod_norm,fit_consts_path)
    norm_consts['AODVISstdn'] = aod_norm

    strataero_forcing.update_strataero(strataero_ds,timestamp,norm_consts,exp_fields) # IN-PLACE update of strataero_ds

    #
    # TO-DO Leo: is it possible to simply overwrite the current forcing file?
    # if not, do you think we should just write a new one and reference that one in the future?
    # 2021-10-01
    #

    # Note LvK: need to write NetCDF3, as NetCDF4 does seem to give errors within CESM
    strataero_ds.to_netcdf(strataero_path, format='NETCDF3_64BIT')


print(timestamp)
#strataero_ds.to_netcdf('foo.nc') 

#
# TO-DO Leo: can you please change the 'nlvals = ...' declaration? This probably feeds the updated forcing file to CESM, right?
# 2021-10-01
#

#nlvals = [ '' ] # TODO

#### WRITE LOG ####

newline = [str(timestamp),str(de[0]),str(sumde[0]),str(l0), # where is 'L0' defined again? is this supposed to be 'l0'?
           str(norm_consts['AODVISstdn']),
           str(norm_consts['so4mass_a1']),str(norm_consts['so4mass_a2']),str(norm_consts['so4mass_a3']),
           str(norm_consts['diamwet_a1']),str(norm_consts['diamwet_a2']),str(norm_consts['diamwet_a3']),
           str(norm_consts['SAD_AERO'])]

if firsttime==1:
    linestowrite=[logheader,newline]
else:
    linestowrite=[]
    for k in range(len(loglines)):
        linestowrite.append(loglines[k])
    linestowrite.append(newline)

writelog(maindir+'/'+logfilename,linestowrite)

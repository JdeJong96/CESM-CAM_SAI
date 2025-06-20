#
# This file contains methods to handle and update the strataero forcing file in each simulation step
#
# created by Daniel Pflueger, d.pfluger@uu.nl on 2021-30-09
#

import xarray as xr
import numpy as np

def _update_variable_in_strataero(strataero_ds,year,variable_name,summand):

    '''
    Updates a specific year's data of a given data variable in a strataero forcing dataset.
    This is done by adding a term to the data variable.
    
    Parameters:
    ---
    strataero_ds (xr.Dataset): strataero Dataset as required by CESM2-CAM6
    year (int): year in which to modify data
    variable_name (string): name of data variable which to modify, e.g. 'so4mass_a3'
    summand (xr.Dataset): Dataset with integer day of year time axis (in a no-leap year).
                          Should contain a data variable compatible with the variable being updated.
                          Must only have a single data variable
                            
    Returns:
    ---
    function is in-place and modifies strataero_ds
    '''
     
    # convert doy axis of summand to cftime 
    year = str(year)
    summand_cftime = xr.cftime_range(start=year+'-01-01',end=year+'-12-31',calendar='noleap')
    summand = summand.rename({'dayofyear': 'time'})
    summand['time'] = summand_cftime
    
    # now weed out the superfluous time steps by masking with the time steps present in strataero_ds
    time_mask = strataero_ds.sel(time=year).time
    summand = summand.sel(time=time_mask)
    
    # change name of data variable in summand to be consistent with the field we want to change
    # this is necessary to use the + operator of xarray
    current_name = list(summand.data_vars)[0]
    summand = summand.rename({current_name: variable_name})
    
    # numpy array of updated data
    updated_data = (strataero_ds + summand)[variable_name].data
    
    # insert updated data into strataero_ds
    # this modification works in-place
    strataero_ds[variable_name].loc[dict(time=time_mask)] = np.clip(updated_data,0.0,None)
    
def _compute_summands(norm_consts,exp_fields):
    
    '''
    Compute summands to be later used in update_strataero by multiplying expected fields with norm factors
    
    Parameters:
    ---
    norm_consts (dict str:float): dictionary of norm constants to multiply with expected fields
    exp_fields (dict str:xr.Dataset): dictionary of expected field Datasets, keys of dictionary must agree with norm_consts
    
    Returns:
    ---
    scaled_fields (dict str:xr.Dataset): dictionary of scaled fields (exp field * norm const). keys are original field names
    '''

    scaled_fields = {}
    
    # iterate over keys in exp_fields dictionary
    # for each of the fields exp_fields[field_name], the associated norm factor is multiplied to the field
    for field_name in exp_fields:
        scaled_fields[field_name] = exp_fields[field_name] * norm_consts[field_name]
        
    return scaled_fields

def update_strataero(strataero_ds,year,norm_consts,exp_fields):
    
    '''
    Wrapper for computing scaled expected fields using norm constants and updating data variables strataero_ds
    
    Parameters:
    ---
    strataero_ds (xr.Dataset): strataero Dataset as required by CESM2-CAM6
    year (int): year which to update in strataero_ds
    norm_consts (dict str:float): dictionary of norm constants to multiply with expected fields. keys must be data variable names in strataero_ds
    exp_fields (dict str:xr.Dataset): dictionary of expected field Datasets, keys of dictionary must agree with norm_consts
 
    Returns:
    ---
    function is in-place and modifies strataero_ds
    '''
    
    scaled_fields = _compute_summands(norm_consts,exp_fields)
    
    for field_name in exp_fields:
        summand = scaled_fields[field_name]
        _update_variable_in_strataero(strataero_ds,year,field_name,summand)
   
    # add a note to strataero_ds that this year has been updated
    # you can use this as a check before executing update_strataero
    # in case the feedback script gets called multiple times in a simulated year
    if not ('feedback_hist' in strataero_ds.attrs.keys()):
        strataero_ds.attrs['feedback_hist'] = str(year)
    else:
        strataero_ds.attrs['feedback_hist'] = strataero_ds.attrs['feedback_hist'] + ' ' + str(year)
        
        
def load_expected_fields(load_path):
    
    '''
    Wrapper for loading expected fields. Note that the names of the files are hardcoded. Pay attention to this if
    you want to exchange the files for some reason.

    Parameters:
    ---
    load_path (str): path relative to working directory containing expected fields. 
                     don't forget the final slash, e.g. './expected_fields/'
    
    Returns:
    ---
    dict str:xr.Dataset: dict of all exp fields, keys being their respective names as in forcing file e.g. 'so4mass_a3' 
    '''
    
    field_names = ['so4mass_a1', 'so4mass_a2', 'so4mass_a3', 
                   'diamwet_a1', 'diamwet_a2', 'diamwet_a3',
                   'SAD_AERO', 'AODVISstdn']
    
    load_names = ['so4_a1', 'so4_a2', 'so4_a3',
                 'dw_a1', 'dw_a2', 'dw_a3',
                 'sad', 'aod']
    
    exp_fields = {}
    
    for field_name, load_name in zip(field_names,load_names):
        exp_fields[field_name] = xr.open_dataset(load_path+load_name)

    return exp_fields
#
# This file provides function to obtain the fitting parameters for the normalization constants
# It requires scipy for the fitting procedure
#
# If you do not want to compute the fitting parameters yourself or scipy is not installed,
# just use the functions all_norms_from_main_field which reads the already computed fitting parameters from a file
#
# Daniel Pflueger, 20.08.21, d.pfluger@uu.nl
#

from scipy.optimize import curve_fit # you might be able to remove this requirement, see the comment in the header
import pickle # needed to save fitting parameters/should be available in python standard installation
import os # in python standard installation

def fit_func_power_law(x,a,b,c):
    '''
    Useful model for the norm constant fitting. It can be applied in all the relevant cases
    
    Parameters:
    x Float: independent variable (in our case either so4a3_mass norm or aod norm)
    a,b,c Float: free parameters later determined by the fit
    
    Returns:
    Float: result of the function
    '''
    return a + b * (x ** c)

def fit_one_norm_const(n_x,n_y,fit_func=fit_func_power_law,p0=None):
    '''
    Fits normalizing constants: n_y(n_x) = fit_func(n_x,*fit params)
    
    Parameters:
    n_y array-like (e.g. xr.DataArray): 
    n_x array-like:
    fit_func function: fit function to be used. Default is fit_func_power_law
    p0 array-like: initial guesses for fit function. if fit_func takes three parameters (a,b,c in the case of fit_func_power_law), you need to give an array of three parameters
    
    Returns:
    Dictionary: dictionary of fit parameters (key ['popt']) and covariance matrix (key ['pcov']). The sqrt of the diagonal entries of the covariance matrix can be related to the standard deviation of the fit parameters
    '''
    
    popt, pcov = curve_fit(fit_func, n_x, n_y, p0=p0)
    
    return {'popt': popt , 'pcov': pcov}
    
def fit_all_norm_const(n_x,n_ys,fit_funcs=None,p0s=None,verbose=True):
    
    '''
    Iterative version of fit_one_norm_const. Relate all norm constants back to the main field
    
    Parameters:
    nx array-like: main normalization constant
    ny array-like containing array-like: list of target normalization constants
    p0s array-like of array-like: initial fit guesses to be used. must contain tuples/list of guesses for every n_y in n_ys
    fit_funcs array-like of functions: fit function to be used for every n_y in n_ys
    verbose Boolean: provides fit parameter output useful for debugging and fitting init guesses
    
    Returns:
    Dictionary: dictionary containing fit results, e.g. results['1']['popt'] will give fit param of 1st fit, where results is output of this functio
    '''
    
    # default init guesses and fit_func (-> will result in fit_func_power_law fit with init guess determined by scipy)
    if not p0s:
        p0s = [None for n_y in n_ys]
    if not fit_funcs:
        fit_funcs = [fit_func_power_law for n_y in n_ys]
    
    # prepare result dictionary
    # e.g. results['1'] will contain the result dictionary of the first fit (with keys 'popt' and 'pcov')
    results = {}
    for (i,n_y) in enumerate(n_ys):
        results[str(i)] = None
    
    for (n_y,p0,fit_func,res_key) in zip(n_ys,p0s,fit_funcs,results):
        fit_dict = fit_one_norm_const(n_x,n_y,fit_func=fit_func,p0=p0)
        if verbose: print('fit ' + str(res_key) + ' ' + str(fit_dict['popt']))
        results[res_key] = fit_dict
        
    return results

def fit_all_norm_const_from_so4mass_a3(exp_so4,exp_dw,exp_sad,fit_funcs=None,p0s=None,save_path='./nc_fit_params/'):
    
    '''
    Convenient wrapper to fit all norm constants (apart from aod) starting from so4mass_a3 & save them for later
    
    Parameters:
    exp_* Dictionary: exp field dictionaries as obtained by the load functions in the norm_const_example.ipynb notebook
    fit_funcs functions: fitting functions for each fit in following order so4mass_a1, *_a2, diamwet_a1, *_a2, *_a3, SAD_AERO
    p0s array-like: init guesses for fit funcs (same order)
    save_path: directory in which to store the fit params of norm constants
    
    Returns:
    Dictionary: fitting param dictionary for all fits. keys are original field names, e.g. SAD_AERO or diamwet_a3
    '''
    
    m1, m2, m3 = exp_so4['a1']['m'], exp_so4['a2']['m'], exp_so4['a3']['m']
    d1, d2, d3 = exp_dw['a1']['m'], exp_dw['a2']['m'], exp_dw['a3']['m']
    sad = exp_sad['sad']['m']

    # perform the fit with so4mass_a3 as main field
    n_x = m3
    n_ys = [m1,m2,d1,d2,d3,sad]
    results = fit_all_norm_const(n_x,n_ys,fit_funcs=fit_funcs,p0s=p0s)
    
    # renaming for convenience
    target_keys = ['so4mass_a1','so4mass_a2','diamwet_a1','diamwet_a2','diamwet_a3','SAD_AERO']
    init_keys = list(results.keys())
    
    for res_key,target_key in zip(init_keys, target_keys):
        results[target_key] = results.pop(res_key)
    
    # saving
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    outfile = open(save_path+'fit_params','wb')
    pickle.dump(results, outfile)
    outfile.close
    
    return results
    
def fit_all_norm_const_from_aod(exp_so4,exp_dw,exp_sad,exp_aod,fit_funcs=None,p0s=None,save_path='./nc_fit_params/'):
    
    '''
    Convenient wrapper to fit all norm constants tarting from AODVISstdn & save them for later
    This is copy/pasted from fit_all_norm_const_from_so4mass_a3 with minor modifications
    
    Parameters:
    exp_* Dictionary: exp field dictionaries as obtained by the load functions in the norm_const_example.ipynb notebook
    fit_funcs functions: fitting functions for each fit in following order so4mass_a1, *_a2, *a3m diamwet_a1, *_a2, *_a3, SAD_AERO
    p0s array-like: init guesses for fit funcs (same order)
    save_path: directory in which to store the fit params of norm constants
    
    Returns:
    Dictionary: fitting param dictionary for all fits. keys are original field names, e.g. SAD_AERO or diamwet_a3
    '''
    
    m1, m2, m3 = exp_so4['a1']['m'], exp_so4['a2']['m'], exp_so4['a3']['m']
    d1, d2, d3 = exp_dw['a1']['m'], exp_dw['a2']['m'], exp_so4['a3']['m']
    sad = exp_sad['sad']['m']
    aod = exp_aod['aod']['m']

    # perform the fit with so4mass_a3 as main field
    n_x = aod
    n_ys = [m1,m2,m3,d1,d2,d3,sad]
    results = fit_all_norm_const(n_x,n_ys,fit_funcs,p0s)
    
    # renaming for convenience
    target_keys = ['so4mass_a1','so4mass_a2','so4mass_a3','diamwet_a1','diamwet_a2','diamwet_a3','SAD_AERO']
    init_keys = list(results.keys())
    
    for res_key,target_key in zip(init_keys, target_keys):
        results[target_key] = results.pop(res_key)
        
    # saving
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    outfile = open(save_path+'fit_params','wb')
    pickle.dump(results, outfile)
    outfile.close
    
    return results

def all_norms_from_main_field(n_x,fit_params_path,fit_funcs=None):
    '''
    Function that returns all norm constants from the main field (AODVISstdn or so4mass_a3) norm constant
    Fit parameters need to be pre computed
    
    Parameters:
    n_x Float: main norm constant
    fit_params_path: path to fit_params pickle file, e.g. ./nc_fit_params/, final slash is required
    fit_funcs: fit funcs to be used (must be consistend with fit param file), default is fit_func_power_law
    
    Returns:
    Dictionary: dictionary of derived norm constants, keys are names from original fields, e.g. 'so4mass_a1' or 'SAD_AERO'
    '''
    
    with open(fit_params_path+'fit_params', 'rb') as infile:
        fit_params = pickle.load(infile)
    
    if not fit_funcs:
        fit_funcs = [fit_func_power_law for fit_param in fit_params]
    
    n_y = {} # result dictionary, e.g. n_y['so4mass_a1'] gives norm constant of so4mass_a1 computed from main field norm
    
    for (field_name,fit_func) in zip(fit_params,fit_funcs):
        n_y[field_name] = fit_func(n_x,*fit_params[field_name]['popt'])
    
    return n_y
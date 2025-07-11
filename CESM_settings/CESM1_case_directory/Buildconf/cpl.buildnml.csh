#! /bin/csh -f

set cwd = `pwd`
cd ${CASEROOT}
source ./Tools/ccsm_getenv || exit -1
cd $cwd

#******************************************************************#
# If the user changes any input datasets - be sure to give it a    #
# unique filename. Do not duplicate any existing input files       #
#******************************************************************#

set exedir = $RUNDIR; cd $exedir

@ atm_cpl_dt = ( 3600 * 24 ) / $ATM_NCPL
@ lnd_cpl_dt = ( 3600 * 24 ) / $LND_NCPL
@ ocn_cpl_dt = ( 3600 * 24 ) / $OCN_NCPL
@ ice_cpl_dt = ( 3600 * 24 ) / $ICE_NCPL
@ glc_cpl_dt = ( 3600 * 24 ) / $GLC_NCPL

set runtype = startup
if ($CONTINUE_RUN == 'TRUE') set runtype = 'continue'
set mybfbflag = '.false.'
if ($BFBFLAG == 'TRUE') set mybfbflag = '.true.'
set mytimbarflag = '.false.'
if ($TIMING_BARRIER == 'TRUE') set mytimbarflag = '.true.'
set mybarrunflag = '.false.'
if ($COMP_RUN_BARRIERS == 'TRUE') set mybarrunflag = '.true.'
set mydobudgets = .false.
if ($BUDGETS == 'TRUE') set mydobudgets = '.true.'
set mydohistinit = .false.
if ($HISTINIT == 'TRUE') set mydohistinit = '.true.'
set mydriverthread = .false.
if ($DRV_THREADING == 'TRUE') set mydriverthread = '.true.'
set mydopole = .true.
if ($SHR_MAP_DOPOLE == 'FALSE') set mydopole = '.false.'
set mybrc = '.false.'
if ($BRNCH_RETAIN_CASENAME == 'TRUE') set mybrc = '.true.'
set mypioasync = .false.
if ($PIO_ASYNC_INTERFACE == 'TRUE') set mypioasync = '.true.'

if ($RUN_TYPE != 'startup' && $CASE == $RUN_REFCASE) then
   if ($BRNCH_RETAIN_CASENAME != 'TRUE') then
      echo "ERROR: CASE and RUN_REFCASE are identical"
      echo "       Set BRNCH_RETAIN_CASENAME to TRUE in env_conf.xml"
      exit -9
   endif
endif

set myocntcoupling = '.false.'
if ($OCN_TIGHT_COUPLING == 'TRUE') set myocntcoupling = '.true.'

set samegrid_ao = '.false.'
set samegrid_ro = '.false.'
set samegrid_al = '.false.'
if ($ATM_GRID == $OCN_GRID) set samegrid_ao = '.true.'
if ($LND_GRID == $OCN_GRID) set samegrid_ro = '.true.'
if ($ATM_GRID == $LND_GRID) set samegrid_al = '.true.'

set profdisable = '.false.'
set profdepth = '20'
if      ($TIMER_LEVEL <= 0) then
  set profdisable = '.true.'
else if ($TIMER_LEVEL >= 1) then
  set profdepth = $TIMER_LEVEL
endif

set pts_settings = " "
if ($PTS_MODE == 'TRUE') then
  set pts_settings = "single_column = .true., scmlat = $PTS_LAT, scmlon = $PTS_LON"
  set samegrid_ao = '.true.'
  set samegrid_ro = '.true.'
  set samegrid_al = '.true.'
endif

if ($COMP_OCN == 'pop2' && $OCN_PIO_ROOT != 0) then
    echo "ERROR: POP2 OCN Component requires OCN_PIO_ROOT==0"
    echo "OCN_PIO_ROOT current setting in env_run.xml is $OCN_PIO_ROOT"
    exit -9
endif



cat >! drv_in << EOF
&seq_infodata_inparm
  case_name     = '$CASE '
  case_desc     = '$CASESTR '
  model_version = '$CCSM_REPOTAG '
  username      = '$CCSMUSER '
  hostname      = '$MACH '
  timing_dir    = './timing'
  tchkpt_dir    = './timing/checkpoints'
  start_type    = '$runtype'
  brnch_retain_casename = $mybrc
  info_debug    = $INFO_DBUG
  bfbflag       = $mybfbflag
  orb_mode        = '$ORBITAL_MODE'
  orb_iyear       = $ORBITAL_YEAR
  orb_iyear_align = $ORBITAL_YEAR_ALIGN
  flux_epbal    = '$CPL_EPBAL'
  flux_albav    = .$CPL_ALBAV.
  samegrid_al   = $samegrid_al
  samegrid_ro   = $samegrid_ro
  samegrid_ao   = $samegrid_ao
  shr_map_dopole = $mydopole
  vect_map      = '$VECT_MAP'
  aoflux_grid   = '$AOFLUX_GRID'
  ocean_tight_coupling = $myocntcoupling
  cpl_cdf64     = .true.
  do_budgets    = $mydobudgets
  do_histinit   = $mydohistinit
  budget_inst   = $BUDGET_INST
  budget_daily  = $BUDGET_DAILY
  budget_month  = $BUDGET_MONTHLY
  budget_ann    = $BUDGET_ANNUAL
  budget_ltann  = $BUDGET_LONGTERM_EOY
  budget_ltend  = $BUDGET_LONGTERM_STOP
  histaux_a2x     = .false.
  histaux_a2x3hr  = .false.
  histaux_a2x3hrp = .false.
  histaux_a2x24hr = .false.
  histaux_l2x     = .false.
  histaux_r2x     = .false.
  drv_threading = $mydriverthread
  run_barriers  = $mybarrunflag
  eps_frac      = $EPS_FRAC
  eps_amask     = $EPS_AMASK
  eps_agrid     = $EPS_AGRID
  eps_aarea     = $EPS_AAREA
  eps_omask     = $EPS_OMASK
  eps_ogrid     = $EPS_OGRID
  eps_oarea     = $EPS_OAREA
  $pts_settings
/ 
&seq_timemgr_inparm
  calendar       = '$CALENDAR'
  atm_cpl_dt     = $atm_cpl_dt
  lnd_cpl_dt     = $lnd_cpl_dt
  ocn_cpl_dt     = $ocn_cpl_dt
  ice_cpl_dt     = $ice_cpl_dt
  glc_cpl_dt     = $glc_cpl_dt
  start_ymd      =  20000101
  start_tod      = $START_TOD
  stop_option    ='$STOP_OPTION'
  stop_n         = $STOP_N
  stop_ymd       = $STOP_DATE
  restart_option ='$REST_OPTION'
  restart_n      = $REST_N
  restart_ymd    = $REST_DATE
  end_restart    = .false.
  history_option ='$HIST_OPTION'
  history_n      = $HIST_N
  history_ymd    = $HIST_DATE
  histavg_option ='$AVGHIST_OPTION'
  histavg_n      = $AVGHIST_N
  histavg_ymd    = $AVGHIST_DATE
  tprof_option   ='$TPROF_OPTION'
  tprof_n        = $TPROF_N
  tprof_ymd      = $TPROF_DATE
/
&ccsm_pes
  atm_ntasks   = $NTASKS_ATM
  atm_nthreads = $NTHRDS_ATM 
  atm_rootpe   = $ROOTPE_ATM
  atm_pestride = $PSTRID_ATM

  lnd_ntasks   = $NTASKS_LND
  lnd_nthreads = $NTHRDS_LND 
  lnd_rootpe   = $ROOTPE_LND
  lnd_pestride = $PSTRID_LND

  ice_ntasks   = $NTASKS_ICE
  ice_nthreads = $NTHRDS_ICE 
  ice_rootpe   = $ROOTPE_ICE
  ice_pestride = $PSTRID_ICE

  ocn_ntasks   = $NTASKS_OCN
  ocn_nthreads = $NTHRDS_OCN 
  ocn_rootpe   = $ROOTPE_OCN
  ocn_pestride = $PSTRID_OCN

  glc_ntasks   = $NTASKS_GLC
  glc_nthreads = $NTHRDS_GLC 
  glc_rootpe   = $ROOTPE_GLC
  glc_pestride = $PSTRID_GLC

  cpl_ntasks   = $NTASKS_CPL
  cpl_nthreads = $NTHRDS_CPL 
  cpl_rootpe   = $ROOTPE_CPL
  cpl_pestride = $PSTRID_CPL
/
&prof_inparm
  profile_disable = $profdisable
  profile_barrier = $mytimbarflag
  profile_single_file = .false.
  profile_depth_limit = $profdepth
  profile_detail_limit = 0
/
!
! NOTE: pio_async_interface=.true. is not yet supported
!
! If pio_async_interface is .true. or {component}_PIO_* variable is not set or set to -99
! the component variable will be set using the pio_* value.
! 
!
&pio_inparm
 pio_async_interface = $mypioasync
 pio_stride          = $PIO_STRIDE  
 pio_root            = $PIO_ROOT
 pio_numtasks        = $PIO_NUMTASKS
 pio_typename        ='$PIO_TYPENAME'
 pio_debug_level     = $PIO_DEBUG_LEVEL

 ocn_pio_stride      = $OCN_PIO_STRIDE  
 ocn_pio_root        = $OCN_PIO_ROOT
 ocn_pio_numtasks    = $OCN_PIO_NUMTASKS
 ocn_pio_typename    ='$OCN_PIO_TYPENAME'

 lnd_pio_stride      = $LND_PIO_STRIDE  
 lnd_pio_root        = $LND_PIO_ROOT
 lnd_pio_numtasks    = $LND_PIO_NUMTASKS
 lnd_pio_typename    ='$LND_PIO_TYPENAME'

 ice_pio_stride      = $ICE_PIO_STRIDE  
 ice_pio_root        = $ICE_PIO_ROOT
 ice_pio_numtasks    = $ICE_PIO_NUMTASKS
 ice_pio_typename    ='$ICE_PIO_TYPENAME'

 atm_pio_stride      = $ATM_PIO_STRIDE  
 atm_pio_root        = $ATM_PIO_ROOT
 atm_pio_numtasks    = $ATM_PIO_NUMTASKS
 atm_pio_typename    ='$ATM_PIO_TYPENAME'

 cpl_pio_stride      = $CPL_PIO_STRIDE  
 cpl_pio_root        = $CPL_PIO_ROOT
 cpl_pio_numtasks    = $CPL_PIO_NUMTASKS
 cpl_pio_typename    ='$CPL_PIO_TYPENAME'

 glc_pio_stride      = $GLC_PIO_STRIDE  
 glc_pio_root        = $GLC_PIO_ROOT
 glc_pio_numtasks    = $GLC_PIO_NUMTASKS
 glc_pio_typename    ='$GLC_PIO_TYPENAME'

/
EOF

# -------------------------------------------------------------------------
echo " - Create modelio namelist input files"
# -------------------------------------------------------------------------

foreach model ($MODELS)
   set moddiri     = $EXEROOT/${model}
   set moddiro     = $RUNDIR
   set modeliofile = ${model}_modelio.nml
   set logfile     = ${model}.log.$LID

cat >! $modeliofile <<EOF
&modelio
   diri    = "$moddiri   "
   diro    = "$moddiro   "
   logfile = "$logfile   "
/
EOF
end

cat >! drv_flds_in << EOF
&drydep_inparm
 drydep_list		= 'H2O2','H2SO4','SO2'
 drydep_method		= 'xactive_atm'
/

EOF

#if ((($GRID =~ *gx*) || ($GRID =~ *tx*)) && ($samegrid_ao == '.false.')) then
#if ($samegrid_ao == '.false.' || $samegrid_al == '.false.' || $samegrid_ro == '.false.') then

#--- set mapping files ---
set map_a2of_file = $MAP_A2OF_FILE
set map_a2os_file = $MAP_A2OS_FILE
set map_o2af_file = $MAP_O2AF_FILE
set map_o2as_file = $MAP_O2AS_FILE
set map_l2af_file = $MAP_L2AF_FILE
set map_l2as_file = $MAP_L2AS_FILE
set map_a2lf_file = $MAP_A2LF_FILE
set map_a2ls_file = $MAP_A2LS_FILE
set map_r2o_file  = $MAP_R2O_FILE_R05

if ($COMP_LND == 'dlnd') then
  if ($DLND_RUNOFF_MODE  == "19BASIN"        ) set map_r2o_file = $MAP_R2O_FILE_R19
  if ($DLND_RUNOFF_MODE  == "DIATREN_ANN_RX1") set map_r2o_file = $MAP_R2O_FILE_RX1
  if ($DLND_RUNOFF_MODE  == "DIATREN_IAF_RX1") set map_r2o_file = $MAP_R2O_FILE_RX1

endif

if ($BFBFLAG == TRUE) then
  set map_a2of_type = X
  set map_a2os_type = X
  set map_o2af_type = X
  set map_o2as_type = X
  set map_l2af_type = X
  set map_l2as_type = X
  set map_a2lf_type = X
  set map_a2ls_type = X
  set map_r2o_type  = X
else
  set map_a2of_type = X
  set map_a2os_type = X
  set map_o2af_type = Y
  set map_o2as_type = Y
  set map_l2af_type = Y
  set map_l2as_type = Y
  set map_a2lf_type = X
  set map_a2ls_type = X
  set map_r2o_type  = Y
endif

rm -f $CASEBUILD/cpl.input_data_list
touch $CASEBUILD/cpl.input_data_list


set mapfilevarname = \
                  (map_a2of_file   map_a2os_file   map_o2af_file   map_o2as_file \
                   map_a2lf_file   map_a2ls_file   map_l2af_file   map_l2as_file \
                   map_r2o_file)

set i = 0
foreach mapfile ($map_a2of_file $map_a2os_file $map_o2af_file $map_o2as_file \
                 $map_a2lf_file $map_a2ls_file $map_l2af_file $map_l2as_file \
                 $map_r2o_file)
  @ i++                
  if ($mapfile != idmap) then  
    if ($mapfile =~ *cpl/gridmaps*) then
       set mapdir = ""
    else
       if ($mapfile =~ */*) then
          echo "ERROR: unsupported mapfile path $mapfile"
          exit -9
       endif
       set mapdir = "cpl/cpl6/"
    endif
cat >> $CASEBUILD/cpl.input_data_list << EOF
$mapfilevarname[$i] = ${DIN_LOC_ROOT}/${mapdir}${mapfile} 
EOF
    set $mapfilevarname[$i] = ${DIN_LOC_ROOT}/${mapdir}${mapfile} 
  endif
end


cat >! seq_maps.rc <<EOF
##################################################################
#
# seq_maps.rc
#
# This is a resource file which lists the names of mapping
# weight files to use in a sequential CCSM run (mapname).
# You can also set when data is rearranged in the mapping (maptype).
#
# This file is read during the map_model2model_init calls.
#
# For maptype:  X = Rearrange the input so that the output
#                   is on the correct processor.
#               Y = Rearrange the output and sum partial outputs
#                   if necessary
#
# NOTE:  For bfb on different processor counts, set all maptypes to "X".
################################################################## 

atm2ocnFmapname: $map_a2of_file
atm2ocnFmaptype: $map_a2of_type

atm2ocnSmapname: $map_a2os_file
atm2ocnSmaptype: $map_a2os_type

ocn2atmFmapname: $map_o2af_file
ocn2atmFmaptype: $map_o2af_type

ocn2atmSmapname: $map_o2as_file
ocn2atmSmaptype: $map_o2as_type

atm2iceFmapname: $map_a2of_file
atm2iceFmaptype: $map_a2of_type

atm2iceSmapname: $map_a2os_file
atm2iceSmaptype: $map_a2os_type

ice2atmFmapname: $map_o2af_file
ice2atmFmaptype: $map_o2af_type

ice2atmSmapname: $map_o2as_file
ice2atmSmaptype: $map_o2as_type

atm2lndFmapname: $map_a2lf_file
atm2lndFmaptype: $map_a2lf_type

atm2lndSmapname: $map_a2ls_file
atm2lndSmaptype: $map_a2ls_type

lnd2atmFmapname: $map_l2af_file
lnd2atmFmaptype: $map_l2af_type

lnd2atmSmapname: $map_l2as_file
lnd2atmSmaptype: $map_l2as_type

rof2ocnFmapname: $map_r2o_file
rof2ocnFmaptype: $map_r2o_type
EOF
#endif

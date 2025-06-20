#! /bin/csh -f

set objdir = $OBJROOT/atm/obj; cd $objdir

set comp = "unknown"
if ($COMP_INTERFACE == 'MCT' ) set comp = mct
if ($COMP_INTERFACE == 'ESMF') set comp = esmf

\cat >! .tmp << EOF; cmp -s .tmp Filepath || mv -f .tmp Filepath 
$CASEROOT/SourceMods/src.cam
/gpfs/home4/renew1/cesm/cesm_tags/cesm1_0_4/models/atm/cam/src/chemistry/pp_trop_mam3
$CODEROOT/atm/cam/src/chemistry/modal_aero
$CODEROOT/atm/cam/src/chemistry/mozart
$CODEROOT/atm/cam/src/chemistry/bulk_aero
$CODEROOT/atm/cam/src/chemistry/utils
$CODEROOT/atm/cam/src/physics/rrtmg
$CODEROOT/atm/cam/src/physics/rrtmg/ext/rrtmg_mcica
$CODEROOT/atm/cam/src/physics/rrtmg/ext/rrtmg_lw
$CODEROOT/atm/cam/src/physics/rrtmg/ext/rrtmg_sw
$CODEROOT/atm/cam/src/physics/cam
$CODEROOT/atm/cam/src/dynamics/fv
$CODEROOT/atm/cam/src/cpl_$comp
$CODEROOT/atm/cam/src/cpl_share
$CODEROOT/atm/cam/src/control
$CODEROOT/atm/cam/src/utils
$CODEROOT/atm/cam/src/utils/pilgrim
EOF

set camdefs = "   -DCO2A -DMAXPATCH_PFT=numpft+1 -DLSMLAT=1 -DLSMLON=1 -DPLON=288 -DPLAT=192 -DPLEV=30 -DPCNST=25 -DPCOLS=16 -DPTRM=1 -DPTRN=1 -DPTRK=1 -DSTAGGERED  -DSPMD -DDUST -DPROGSSLT -DMODAL_AERO -DMODAL_AERO_3MODE "
gmake complib -j $GMAKE_J MODEL=cam COMPLIB=$LIBROOT/libatm.a MACFILE=$CASEROOT/Macros.$MACH USER_CPPDEFS="$camdefs" -f $CASETOOLS/Makefile || exit 2

wait


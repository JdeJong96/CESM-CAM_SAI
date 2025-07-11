#! /bin/csh -f

#--------------------------------------------------------------------
# check basic task and thread settings
#--------------------------------------------------------------------

set exedir  = $RUNDIR
set rundir  = $RUNDIR
set objdir  = $OBJROOT/ocn/obj
set ocndir  = $RUNDIR
set srcdir  = $CODEROOT/ocn/pop2
set my_path = $CASEROOT/SourceMods/src.pop2

set ntask   = $NTASKS_OCN
set ocn_tracers = (`echo $OCN_TRACER_MODULES`)

setenv OCN_PRESTAGE FALSE
setenv INPUT        $EXEROOT/ocn/input
setenv POP2_DOCDIR  $CASEBUILD/pop2doc
setenv POP2_BLDNML  $POP2_DOCDIR/document_pop2_buildnml
setenv runtype      $RUN_TYPE

setenv OCN_GRID gx1v6 # used in ocn.*.setup.csh scripts

cd $objdir

echo -------------------------------------------------------------------------
echo Begin the process of building the pop2 executable
echo -------------------------------------------------------------------------
echo " "

setenv BLCKX $POP_BLCKX
setenv BLCKY $POP_BLCKY
setenv MXBLCKS $POP_MXBLCKS
setenv DECOMPTYPE $POP_DECOMPTYPE

echo -----------------------------------------------------------------
echo Create the internal directory structure
echo -----------------------------------------------------------------

set compile_dir = $objdir
set source_dir  = $OBJROOT/ocn/source

if !(-d $source_dir  ) mkdir -p $source_dir
if !(-d $compile_dir ) mkdir -p $compile_dir

echo -----------------------------------------------------------------
echo Create domain_size.F90 in $source_dir, first computing NT
echo -----------------------------------------------------------------

echo 2 > $source_dir/NT
foreach module ( $ocn_tracers )
  if (-f ${my_path}/ocn.${module}.setup.csh) then
     ${my_path}/ocn.${module}.setup.csh set_nt $source_dir/NT || exit $status
  else if (-f $srcdir/input_templates/ocn.${module}.setup.csh ) then
     $srcdir/input_templates/ocn.${module}.setup.csh set_nt $source_dir/NT || exit $status
  else
     echo error in pop.buildexe.csh unknown tracer: $module
     exit -3
  endif
end
set NT = `cat $source_dir/NT`

if (-f ${my_path}/gx1v6_domain_size.F90) then
   set domain_size_infile = ${my_path}/gx1v6_domain_size.F90
else
   set domain_size_infile = $srcdir/input_templates/gx1v6_domain_size.F90
endif

#
#  If new domain_size.F90 is identical to existing one, do nothing.
#  This is in order to preserve file timestamps and avoid unnecessary
#  compilation cascade.
#

sed -e "s#nt *= *2#nt = $NT#" < $domain_size_infile > $source_dir/domain_size.F90.new
if (-f $source_dir/domain_size.F90) then
  diff $source_dir/domain_size.F90.new $source_dir/domain_size.F90
  if ($status) then
    mv $source_dir/domain_size.F90.new $source_dir/domain_size.F90
    cp ${my_path}/gx1v6_domain_size.F90 domain_size.F90
  else
    rm -f $source_dir/domain_size.F90.new
  endif
else
  mv $source_dir/domain_size.F90.new $source_dir/domain_size.F90
  cp ${my_path}/gx1v6_domain_size.F90 domain_size.F90
endif

############### needed during LANL merge transition #####################
if (-f ${my_path}/gx1v6_POP_DomainSizeMod.F90) then
   cp -fp  ${my_path}/gx1v6_POP_DomainSizeMod.F90 $source_dir/POP_DomainSizeMod.F90
else
   cp -fp $srcdir/input_templates/gx1v6_POP_DomainSizeMod.F90 $source_dir/POP_DomainSizeMod.F90
endif
######################### end LANL merge transition #####################

echo -----------------------------------------------------------------
echo  Copy the necessary files into $source_dir                     
echo -----------------------------------------------------------------
cd $source_dir
cp -fp $srcdir/source/*.F90                .
cp -fp $srcdir/mpi/*.F90                   .
cp -fp $srcdir/drivers/cpl_share/*.F90     .
if ($COMP_INTERFACE == 'MCT') then
  cp -fp $srcdir/drivers/cpl_mct/*.F90     .
else if ($COMP_INTERFACE == 'ESMF') then
  cp -fp $srcdir/drivers/cpl_esmf/*.F90    .
else
  echo "ERROR: must specifiy valid $COMP_INTERFACE value"
  exit -1
endif
if (-d $my_path ) cp -fp $my_path/*.F90   .
rm -f gx1v6_domain_size.F90
#
#  recompile if 2d decomp is changed
#
set recompile = FALSE
echo gx1v6 $ntask ${BLCKX} ${BLCKY} ${MXBLCKS} >! $objdir/ocnres.new
diff $objdir/ocnres.new $objdir/ocnres.old || set recompile = TRUE
if ($recompile == 'TRUE') then
    touch `grep -l BLCKX $source_dir/*`  # force recompile
    touch `grep -l BLCKY $source_dir/*`  # force recompile
    touch `grep -l MXBLCKS $source_dir/*`  # force recompile
endif  
echo gx1v6 $ntask ${BLCKX} ${BLCKY} ${MXBLCKS} >! $objdir/ocnres.old

echo -----------------------------------------------------------------
echo  Compile pop2 library
echo -----------------------------------------------------------------
cd $compile_dir
\cat >! Filepath <<EOF
 $source_dir
EOF

cd $compile_dir

set pop2defs = "-DCCSMCOUPLED -DBLCKX=$BLCKX -DBLCKY=$BLCKY -DMXBLCKS=$MXBLCKS"
if ($OCN_ICE_FORCING == 'inactive' ) then
set pop2defs = "$pop2defs -DZERO_SEA_ICE_REF_SAL"
endif

if ($OCN_GRID =~ tx0.1* ) then
set pop2defs = "$pop2defs -D_HIRES"
endif

gmake complib -j $GMAKE_J MODEL=pop2 COMPLIB=$LIBROOT/libocn.a MACFILE=$CASEROOT/Macros.$MACH USER_CPPDEFS="$pop2defs" -f $CASETOOLS/Makefile || exit 2

set f90_dir = $source_dir/f90
if !(-d  $f90_dir ) mkdir -p $f90_dir

echo " "
echo ----------------------------------------------------------------------------
echo  Note that f90 files may not exist on all machines
echo ----------------------------------------------------------------------------
mv -f *.f90 $f90_dir

if !(-f $LIBROOT/libocn.a) then
  echo "ERROR: pop2 library not available"
  exit -1
endif

echo " "
echo -------------------------------------------------------------------------
echo  Successful completion of the pop2 executable building process
echo -------------------------------------------------------------------------

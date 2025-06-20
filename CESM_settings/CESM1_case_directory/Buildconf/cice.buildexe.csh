#! /bin/csh -f 

set objdir = $OBJROOT/ice/obj; cd $objdir

set comp = "unknown"
if ($COMP_INTERFACE == 'MCT' ) set comp = mct
if ($COMP_INTERFACE == 'ESMF') set comp = esmf

\cat >! .tmp << EOF; cmp -s .tmp Filepath || mv -f .tmp Filepath 
$CASEROOT/SourceMods/src.cice
$CODEROOT/ice/cice/src/drivers/cpl_$comp
$CODEROOT/ice/cice/src/drivers/cpl_share
$CODEROOT/ice/cice/src/mpi
$CODEROOT/ice/cice/src/source
EOF

# Check for recompile if BLCKX, BLCKY or MXBLCKS changes
#-------------------------------------------------------
set recompile = FALSE
echo ${CICE_BLCKX} ${CICE_BLCKY} ${CICE_MXBLCKS} > $objdir/iceres.new
cmp -s $objdir/iceres.new $objdir/iceres.old || set recompile = TRUE
if ($recompile == 'TRUE') then
  cat $objdir/iceres.old
  cat $objdir/iceres.new
  echo "blckx,blcky,mxblcks has changed, removing objdir and cice, preparing for new compile"
  rm -f $objdir/*.o
  rm -f $objdir/*.f
  rm -f $objdir/*.f90
endif

# Build the library
#-------------------------------------------------------
set cicedefs = "  -DCCSMCOUPLED -Dcoupled -Dncdf -DNCAT=5 -DNXGLOB=320 -DNYGLOB=384 -DNTR_AERO=3"
set cicedefs = "$cicedefs -DBLCKX=$CICE_BLCKX -DBLCKY=$CICE_BLCKY -DMXBLCKS=$CICE_MXBLCKS"        
gmake complib -j $GMAKE_J MODEL=cice COMPLIB=$LIBROOT/libice.a MACFILE=$CASEROOT/Macros.$MACH USER_CPPDEFS="$cicedefs" -f $CASETOOLS/Makefile || exit 2

mv $objdir/iceres.new $objdir/iceres.old

wait 
exit 0

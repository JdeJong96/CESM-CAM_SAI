#! /bin/csh -f 

set objdir = $OBJROOT/glc/obj; cd $objdir
set comp = 'unknown'
if ($COMP_INTERFACE == 'MCT' ) set comp = mct
if ($COMP_INTERFACE == 'ESMF') set comp = esmf

#------------------------------------------------------------------------------
# Build the library
#------------------------------------------------------------------------------
cat >! Filepath << EOF
$CASEROOT/SourceMods/src.sglc
$CODEROOT/glc/sglc
$CODEROOT/glc/sglc/cpl_$comp
EOF

gmake complib -j $GMAKE_J MODEL=sglc COMPLIB=$LIBROOT/libglc.a -f $CASETOOLS/Makefile MACFILE=$CASEROOT/Macros.$MACH || exit 2


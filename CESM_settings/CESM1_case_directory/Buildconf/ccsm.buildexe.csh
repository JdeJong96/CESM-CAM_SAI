#! /bin/csh -f 

set objdir = $OBJROOT/ccsm/obj; cd $objdir

echo -------------------------------------------------------------------------
echo " Building a single executable version of CCSM "
echo -------------------------------------------------------------------------

\cat >! Filepath << EOF
$CASEROOT/SourceMods/src.drv
$CODEROOT/drv/driver
EOF

gmake exec_se -j $GMAKE_J EXEC_SE=$RUNDIR/ccsm.exe MODEL=driver MACFILE=$CASEROOT/Macros.$MACH -f $CASETOOLS/Makefile || exit 2


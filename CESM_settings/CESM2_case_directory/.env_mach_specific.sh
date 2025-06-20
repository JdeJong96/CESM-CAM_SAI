# This file is for user convenience only and is not used by the model
# Changes to this file will be ignored and overwritten
# Changes to the environment should be made in env_mach_specific.xml
# Run ./case.setup --reset to regenerate this file
source /usr/share/Modules/init/sh
module load 2021 CMake/3.20.1-GCCcore-10.3.0 netCDF-Fortran/4.5.3-gompi-2021a netCDF/4.8.0-gompi-2021a FlexiBLAS/3.0.4-GCC-10.3.0 NCO/5.0.1-foss-2021a
export OMP_STACKSIZE=256M
export MPI_TYPE_DEPTH=16
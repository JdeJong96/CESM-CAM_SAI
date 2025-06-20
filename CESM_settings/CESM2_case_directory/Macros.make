ifeq ($(COMPILER),gnu)
  SUPPORTS_CXX := TRUE
  CFLAGS :=  -std=gnu99 -march=native
  CXX_LINKER := FORTRAN
  FC_AUTO_R8 :=  -fdefault-real-8 
  FFLAGS :=   -fconvert=big-endian -ffree-line-length-none -ffixed-line-length-none -fallow-argument-mismatch -fallow-invalid-boz -march=native
  FFLAGS_NOOPT :=  -O0 
  FIXEDFLAGS :=   -ffixed-form 
  FREEFLAGS :=  -ffree-form 
  HAS_F2008_CONTIGUOUS := FALSE
  MPICC := mpicc
  MPICXX := mpicxx
  MPIFC := mpif90
  SCC :=  gcc 
  SCXX :=  g++ 
  SFC :=  gfortran 
  NETCDF_C_PATH := /sw/arch/Centos8/EB_production/2021/software/netCDF/4.8.0-gompi-2021a/
  NETCDF_FORTRAN_PATH := /sw/arch/Centos8/EB_production/2021/software/netCDF-Fortran/4.5.3-gompi-2021a/
  CONFIG_ARGS :=  --host=Linux 
endif
ifeq ($(COMPILER),intel)
  FIXEDFLAGS :=  -fixed -132 
  FREEFLAGS :=  -free 
  CXX_LDFLAGS :=  -cxxlib 
endif
ifeq ($(MODEL),pop)
  CPPDEFS := $(CPPDEFS)  -D_USE_FLOW_CONTROL 
endif
ifeq ($(COMPILER),gnu)
  CPPDEFS := $(CPPDEFS)  -DFORTRANUNDERSCORE -DNO_R16 -DCPRGNU
  CPPDEFS := $(CPPDEFS)  -DLINUX 
  SLIBS := $(SLIBS) -lnetcdf -lnetcdff -lflexiblas
  ifeq ($(compile_threaded),true)
    CFLAGS := $(CFLAGS)  -fopenmp 
    FFLAGS := $(FFLAGS)  -fopenmp 
  endif
  ifeq ($(DEBUG),TRUE)
    CFLAGS := $(CFLAGS)  -g -Wall -Og -fbacktrace -ffpe-trap=invalid,zero,overflow -fcheck=bounds 
    FFLAGS := $(FFLAGS)  -g -Wall -Og -fbacktrace -ffpe-trap=zero,overflow -fcheck=bounds 
  endif
  ifeq ($(DEBUG),FALSE)
    CFLAGS := $(CFLAGS)  -O 
    FFLAGS := $(FFLAGS)  -O 
  endif
  ifeq ($(compile_threaded),true)
    LDFLAGS := $(LDFLAGS)  -fopenmp 
    LDFLAGS := $(LDFLAGS)  -fopenmp 
  endif
endif
ifeq ($(COMPILER),intel)
  CPPDEFS := $(CPPDEFS)  -DFORTRANUNDERSCORE -DCPRINTEL
  ifeq ($(MPILIB),mpich)
    SLIBS := $(SLIBS)  -mkl=cluster 
  endif
  ifeq ($(MPILIB),mpich2)
    SLIBS := $(SLIBS)  -mkl=cluster 
  endif
  ifeq ($(MPILIB),mvapich)
    SLIBS := $(SLIBS)  -mkl=cluster 
  endif
  ifeq ($(MPILIB),mvapich2)
    SLIBS := $(SLIBS)  -mkl=cluster 
  endif
  ifeq ($(MPILIB),mpt)
    SLIBS := $(SLIBS)  -mkl=cluster 
  endif
  ifeq ($(MPILIB),openmpi)
    SLIBS := $(SLIBS)  -mkl=cluster 
  endif
  ifeq ($(MPILIB),impi)
    SLIBS := $(SLIBS)  -mkl=cluster 
  endif
  ifeq ($(MPILIB),mpi-serial)
    SLIBS := $(SLIBS)  -mkl 
  endif
  ifeq ($(compile_threaded),true)
    LDFLAGS := $(LDFLAGS)  -qopenmp 
  endif
endif

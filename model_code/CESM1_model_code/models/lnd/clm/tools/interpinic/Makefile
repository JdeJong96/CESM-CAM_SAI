#-----------------------------------------------------------------------
# This Makefile is for building clm tools on AIX, Linux (with pgf90 or 
# lf95 compiler), Darwin or IRIX platforms.
#
# These macros can be changed by setting environment variables:
#
# LIB_NETCDF --- Library directory location of netcdf. (defaults to /usr/local/lib)
# INC_NETCDF --- Include directory location of netcdf. (defaults to /usr/local/include)
# MOD_NETCDF --- Module directory location of netcdf.  (defaults to $LIB_NETCDF)
# USER_FC ------ Allow user to override the default Fortran compiler specified in Makefile.
# USER_FCTYP --- Allow user to override the default type of Fortran compiler (linux and USER_FC=ftn only).
# USER_CC ------ Allow user to override the default C compiler specified in Makefile (linux only).
# USER_LINKER -- Allow user to override the default linker specified in Makefile.
# USER_CPPDEFS - Additional CPP defines.
# USER_CFLAGS -- Additional C compiler flags that the user wishes to set.
# USER_FFLAGS -- Additional Fortran compiler flags that the user wishes to set.
# USER_LDLAGS -- Additional load flags that the user wishes to set.
# SMP ---------- Shared memory Multi-processing (TRUE or FALSE) [default is FALSE]
# OPT ---------- Use optimized options.
#
#------------------------------------------------------------------------

# Set up special characters
null  :=

EXENAME = interpinic
RM = rm

# Check for the netcdf library and include directories 
ifeq ($(LIB_NETCDF),$(null))
  LIB_NETCDF := /usr/local/lib
endif

ifeq ($(INC_NETCDF),$(null))
  INC_NETCDF := /usr/local/include
endif

ifeq ($(MOD_NETCDF),$(null))
  MOD_NETCDF := $(LIB_NETCDF)
endif

# Set user specified Fortran compiler
ifneq ($(USER_FC),$(null))
  FC := $(USER_FC)
endif
# Set user specified C compiler
ifneq ($(USER_CC),$(null))
  CC := $(USER_CC)
endif

# Set if Shared memory multi-processing will be used
ifeq ($(SMP),$(null))
  SMP := FALSE
endif

CPPDEF := -DNO_SHR_VMATH $(USER_CPPDEFS)

ifeq ($(OPT),$(null))
   # Set optimization on by default
   OPT := TRUE
endif

ifeq ($(OPT),FALSE)
else
   CPPDEF += -DOPT
endif

# Determine platform 
UNAMES := $(shell uname -s)

# Load dependency search path.
dirs := . $(shell cat Filepath)

# Set cpp search path, include netcdf
cpp_dirs := $(dirs) $(INC_NETCDF) $(INC_MPI) $(MOD_NETCDF)
cpp_path := $(foreach dir,$(cpp_dirs),-I$(dir)) # format for command line

# Expand any tildes in directory names. Change spaces to colons.
VPATH    := $(foreach dir,$(cpp_dirs),$(wildcard $(dir))) 
VPATH    := $(subst $(space),:,$(VPATH))               

#Primary Target: build the tool
all: $(EXENAME)

# Get list of files and build dependency file for all .o files
#   using perl scripts mkSrcfiles and Mkdepends

SOURCES   := $(shell cat Srcfiles)

OBJS      := $(addsuffix .o, $(basename $(SOURCES)))

# Newer makes set the CURDIR variable.
CURDIR := $(shell pwd)

ifeq ($(TOOLROOT),$(null))
   ifeq ($(CLM_ROOT),$(null))
      TOOLROOT := $(CURDIR)
   else
      TOOLROOT := $(CLM_ROOT)/models/lnd/clm/tools/$(EXENAME)
   endif
endif


$(CURDIR)/Depends: $(CURDIR)/Srcfiles $(CURDIR)/Filepath
	$(TOOLROOT)/Mkdepends Filepath Srcfiles > $@


# Architecture-specific flags and rules
#------------------------------------------------------------------------
# AIX
#------------------------------------------------------------------------

ifeq ($(UNAMES),AIX)
CPPDEF += -DAIX -DFORTRAN_SAME
cpre = $(null)-WF,-D$(null)
FPPFLAGS   := $(patsubst -D%,$(cpre)%,$(CPPDEF))
LIB_NETCDF := /usr/local/lib64/r4i4
FFLAGS  = -c -I$(INC_NETCDF) -q64 -qsuffix=f=f90 -qsuffix=f=f90:cpp=F90 \
	   $(FPPFLAGS)  -g -qfullpath
LDFLAGS = -L$(LIB_NETCDF) -q64 -lnetcdf
ifneq ($(OPT),TRUE)
   FFLAGS  += -qinitauto=FF911299 -qflttrap=ov:zero:inv:en -C
else
   FFLAGS  += -O2 -qmaxmem=-1 -Q
   LDFLAGS += -Q
endif
CFLAGS  := -q64 -g $(CPPDEF) -O2
FFLAGS += $(cpp_path)
CFLAGS += $(cpp_path)

ifeq ($(SMP),TRUE)
  FC       = xlf90_r
  FFLAGS  += -qsmp=omp
  LDFLAGS += -qsmp=omp
else
  FC       = xlf90
endif

endif

#------------------------------------------------------------------------
# Darwin
#------------------------------------------------------------------------

ifeq ($(UNAMES),Darwin)

# Set the default Fortran compiler
ifeq ($(USER_FC),$(null))
  FC := g95
endif
ifeq ($(USER_CC),$(null))
  CC := gcc
endif

CFLAGS  := -g -O2
CPPDEF  += -DSYSDARWIN -DDarwin -DLINUX
LDFLAGS :=

ifeq ($(FC),g95)

   CPPDEF   += -DFORTRAN_SAME
   CPPDEF   += -DG95
   FFLAGS   := -c -fno-second-underscore $(CPPDEF) $(cpp_path) -I$(MOD_NETCDF)
   ifeq ($(OPT),TRUE)
     FFLAGS += -O2
   else
     FFLAGS += -g -fbounds-check
   endif

endif

ifeq ($(FC),gfortran)

   CPPDEF   += -DG95
   CPPDEF   += -DFORTRAN_SAME
   FFLAGS   := -c -fno-second-underscore $(CPPDEF) $(cpp_path) -I$(MOD_NETCDF) \
               -fno-range-check
   ifeq ($(OPT),TRUE)
     FFLAGS += -O2
   else
     FFLAGS += -g -fbounds-check
   endif

endif

ifeq ($(FC),ifort)

  CPPDEF  += -DFORTRANUNDERSCORE
  FFLAGS  += -c -ftz -g -fp-model precise $(CPPDEF) $(cpp_path) \
             -convert big_endian -assume byterecl -traceback -FR
  LDFLAGS += -m64

  ifneq ($(OPT),TRUE)
     FFLAGS    += -CB -O0
  else
     FFLAGS    += -O2
  endif
  ifeq ($(SMP),TRUE)
    FFLAGS    += -openmp
    LDFLAGS   += -openmp
  endif
endif

ifeq ($(FC),pgf90)

  CPPDEF  += -DFORTRANUNDERSCORE
  FFLAGS  += -c $(CPPDEF) $(cpp_path)
  ifneq ($(OPT),TRUE)
    FFLAGS += -g -Ktrap=fp -Mbounds -Kieee
  else
    FFLAGS += -fast -Kieee
  endif

  ifeq ($(SMP),TRUE)
    FFLAGS   += -mp
    LDFLAGS  += -mp
  endif

endif

ifeq ($(CC),icc)
   CFLAGS     += -m64 -g
   ifeq ($(SMP),TRUE)
     CFLAGS    += -openmp
   endif
endif
ifeq ($(CC),pgcc)
  CFLAGS     += -g -fast
endif

CFLAGS  += $(CPPDEF) $(cpp_path)
LDFLAGS += -L$(LIB_NETCDF) -lnetcdf -lSystemStubs -lSystemStubs_profile

endif

#------------------------------------------------------------------------
# Linux
#------------------------------------------------------------------------

ifeq ($(UNAMES),Linux)
  ifeq ($(USER_FC),$(null))
    #FC    := pgf90
    #FCTYP   := pgf90
    FC    := mpif90
    FCTYP   := mpif90
    NETCDF_PATH = /home/renew1/cesm/cesm_tags/cesm1_0_4/scripts/netcdf_libs/
    INC_NETCDF    := $(NETCDF_PATH)/include
    LIB_NETCDF    := $(NETCDF_PATH)/lib
  else 
  ifeq ($(USER_FC),ftn)
      ifneq ($(USER_FCTYP),$(null))
         FCTYP := $(USER_FCTYP)
      else
         FCTYP := pgf90
      endif
    else
      FCTYP := $(USER_FC)
    endif
  endif
  CPPDEF += -DLINUX -DFORTRANUNDERSCORE -DNO_R16 -DNO_SHR_VMATH
  CFLAGS := $(CPPDEF)
  LDFLAGS = -L$(LIB_NETCDF) -lnetcdf -lnetcdff
  FFLAGS = $(CPPDEFS) -g -O0 -fconvert=big-endian -fallow-invalid-boz -ffree-line-length-none -fallow-argument-mismatch -fno-range-check -fno-unsafe-math-optimizations -frounding-math -fsignaling-nans -fbacktrace -DISNAN_INTRINSIC

  ifeq ($(FCTYP),pgf90)
    CC     := pgcc
    ifneq ($(OPT),TRUE)
      FFLAGS += -g -Ktrap=fp -Mbounds -Kieee
    else
      FFLAGS += -fast -Kieee
      CFLAGS += -fast
    endif

    ifeq ($(SMP),TRUE)
      FFLAGS   += -mp
      LDFLAGS  += -mp
    endif

  endif

  ifeq ($(FCTYP),lf95)
    ifneq ($(OPT),TRUE)
      FFLAGS += -g --chk a,e,s,u -O0
    else
      FFLAGS += -O
    endif
    # Threading only works by putting thread memory on the heap rather than the stack
    # (--threadheap).
    # As of lf95 version 6.2 the thread stacksize limits are (still) too small to run
    # even small
    # resolution problems (FV at 10x15 res fails).
    ifeq ($(SMP),TRUE)
      FFLAGS  += --openmp --threadheap 4096
      LDFLAGS += --openmp --threadheap 4096
    endif
  endif
  ifeq ($(FCTYP),pathf90)
    FFLAGS += -extend_source -ftpp -fno-second-underscore
    ifneq ($(OPT),TRUE)
      FFLAGS += -g -O0
    else
      FFLAGS += -O
    endif
    ifeq ($(SMP),TRUE)
      FFLAGS   += -mp
      LDFLAGS  += -mp
    endif
  endif
  ifeq ($(FCTYP),ifort)

    FFLAGS      += -ftz -g -fp-model precise -convert big_endian -assume byterecl -traceback -FR
    CFLAGS      += -m64 -g
    LDFLAGS   += -m64

    ifneq ($(OPT),TRUE)
       FFLAGS    += -CB -O0
    else
       FFLAGS    += -O2
    endif
    ifeq ($(SMP),TRUE)
      FFLAGS    += -openmp
      CFLAGS    += -openmp
      LDFLAGS   += -openmp
    endif
  endif
  FFLAGS += -c -I$(INC_NETCDF) $(CPPDEF) $(cpp_path)
  CFLAGS += $(cpp_path)
endif

#------------------------------------------------------------------------
# Default rules and macros
#------------------------------------------------------------------------

.SUFFIXES:
.SUFFIXES: .F90 .c .o

# Append user defined compiler and load flags to Makefile defaults
CFLAGS   += $(USER_CFLAGS)
FFLAGS   += $(USER_FFLAGS)
LDFLAGS  += $(USER_LDFLAGS)

# Set user specified linker
ifeq ($(USER_LINKER),$(null))
  LINKER := $(FC)
else
  LINKER := $(USER_LINKER)
endif

.F90.o:
	$(FC) $(FFLAGS) $<

.c.o:
	$(CC) -c $(CFLAGS) $<


$(EXENAME): $(OBJS)
	$(LINKER) -o $@ $(OBJS) $(LDFLAGS)

clean:
	$(RM) -f $(OBJS) *.mod Depends

include $(CURDIR)/Depends

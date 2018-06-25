OS=$(shell uname -s)

# The C compiler options are only used when compiling reference
# (non-Futhark) benchmarks.
CC?=gcc
ifeq ($(OS),Darwin)
  CFLAGS=-framework OpenCL -O3 -std=c99
else
  CFLAGS=-lOpenCL -O3 -std=c99
endif

# On macOS, prefer an AMD device.  On other systems, just pick the
# first one.
ifeq ($(OS),Darwin)
  FUTHARK_OPENCL_DEVICE?=AMD
else
  FUTHARK_OPENCL_DEVICE?=
endif

AUTOTUNE_SECONDS=1200 # 20 minutes at most.

# If this is bin/futhark-opencl, it will be automatically built (if
# necessary) when running the benchmarks.  Otherwise, set it to
# 'futhark-opencl' to use the globally installed one.
FUTHARK_OPENCL=bin/futhark-opencl

# Same behaviour as FUTHARK_OPENCL.
FUTHARK_C=bin/futhark-c

export

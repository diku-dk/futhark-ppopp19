# This file is included both by config.mk and tools, so keep it polyglot.

# If this is bin/futhark-opencl, it will be automatically built (if
# necessary) when running the benchmarks.  Otherwise, set it to
# 'futhark-opencl' to use the globally installed one.
FUTHARK_OPENCL=bin/futhark-opencl

# Same behaviour as FUTHARK_OPENCL.
FUTHARK_C=bin/futhark-c

# Same behaviour as FUTHARK_OPENCL.
FUTHARK_DATASET=bin/futhark-dataset

# Same behaviour as FUTHARK_OPENCL.
FUTHARK_BENCH=bin/futhark-bench

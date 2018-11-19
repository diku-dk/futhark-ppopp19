**IMPORTANT: IF YOU CLONE THIS REPOSITORY, USE `--recursive`, OR INITIALISE GIT SUBMODULES MANUALLY AFTERWARDS.**

# Experimental infrastructure for PPOPP'19 paper

Due to issues with making OpenCL/CUDA available in a VM image, this
infrastructure depends on some fairly common tools and libraries being
installed on the local system.  Specifically, we require:

  * [The Haskell Tool Stack](https://docs.haskellstack.org) for
    building the Futhark compiler itself.  The [installation
    instructions](https://docs.haskellstack.org/en/stable/README/#how-to-install)
    tend to work.

  * The OpenTuner Python libraries must be installed, which can be
    done with `pip install opentuner`.

  * OpenTuner depends on [SQLite](https://www.sqlite.org/index.html),
    which must also be installed.  SQLite can be found in the package
    system of virtually any Linux distribution.

## Usage

Ideally, run `make` and everything will happen.  All external
resources are automatically be downloaded with `git` and `wget` if
necessary.  Results will be located in machine-readable form in the
`results/` directory, auto-tuned parameters in `tunings/`, and graphs
will be produced in PDF format in the root directory.

The `config.mk` file contains commented configuration parameters that
may need customisation based on the machine being used.  In
particular, you may need to increase the time allotted to auto-tuning
in order to reach the results from the paper, depending on the speed
of the machine (and how lucky you are).

## System requirements

The main requirement is a working OpenCL installation; specifically
one that can compile without passing many weird flags or options to
the compiler.  We expect that on Linux, an OpenCL program can be
compiled with

    gcc foo.c -lOpenCL

and on macOS with

    gcc foo.c -framework OpenCL

A quick way to determine whether the system is sound is to run

    make bin/gpuid

One some systems, depending on the OpenCL vendor, it may be necessary
to set some combination of the environment variables `LIBRARY_PATH`,
`CPATH`, and `LD_LIBRARY_PATH` for this to work.

You will need a relatively beefy GPU, as in particular LocVolCalib is
memory-hungry when being auto-tuned.  3GiB should be enough.

While Futhark-generated code can handle multiple available OpenCL
platforms, most of the third party benchmark implementations look only
at the first platform.  These may fail if the device name indicated in
`config.mk` is not part of the first platform.  On most systems, this
will not be an issue, but it may be worth looking at the contents of
`/etc/OpenCL/vendors`, or using the [clinfo] tool, which is available
in many package systems.

[clinfo]: https://github.com/Oblomov/clinfo

For generating the graphs, you will also need Python with Matplotlib,
Numpy, as well as a standard working LaTeX setup.

For building the Futhark compiler you will need [stack], a build
tool for Haskell.  You can possibly also install a binary release of
Futhark, and modify `config.mk` to use that instead.  However, a
future (or past) release Futhark may not match the one this benchmark
suite was designed for.

[stack]: https://docs.haskellstack.org

You will also need [OpenTuner] installed.  This is usually
accomplished simply by running

    pip install opentuner

[OpenTuner]: http://opentuner.org/

## Other `make` targets

In case not the entire suite able to execute on a given system, there
are some useful sub-targets that can be used to run just parts:

  `make matmul-runtimes-large.pdf` and `make
  matmul-runtimes-small.pdf`: run the matrix multiplication benchmark.

  `LocVolCalib-runtimes.pdf`: run the LocVolCalib benchmark.

  `bulk-impact-speedup.pdf`: run both Futhark and reference versions
  of the various Rodinia and Parboil benchmarks.  This is perhaps the
  one most likely to fail, as it involves a significant amount of
  third party code, not all of which was designed with benchmarking
  and portability in mind.

  `veryclean`: like `clean`, but removes even the parts that have been
  downloaded externally.

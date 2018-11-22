**IMPORTANT: IF YOU CLONE THIS REPOSITORY, USE `--recursive`, OR INITIALISE GIT SUBMODULES MANUALLY AFTERWARDS.**

# Experimental infrastructure for PPOPP'19 paper

## Docker image

We provide a Docker image with the necessary programs and libraries
for Futhark to build and run.  This currently only works on Linux
machines with Nvidia GPUs.  Install:

  * [Docker](https://docs.docker.com/install/)
  * [Nvidia's Docker runtime](https://github.com/NVIDIA/nvidia-docker#quickstart)

Run:

```
docker run -it --runtime=nvidia futhark/ppopp19
```

(You may need to use `sudo` or similar for this.)

You should now have a shell open inside a directory with the contents of
this repository.  Next step: [Usage](#usage).

(Alternatively you can build the Docker image yourself by using the
Dockerfile included in this repository.)


## Manual installation of dependencies

*In case you don't use the Docker image:*

This infrastructure depends on some fairly common tools and libraries
being installed on the local system.  Specifically, we require:

  * [The Haskell Tool Stack](https://docs.haskellstack.org) for
    building the Futhark compiler itself.  The [installation
    instructions](https://docs.haskellstack.org/en/stable/README/#how-to-install)
    tend to work.

  * The OpenTuner Python libraries must be installed, which can be
    done with `pip install --user opentuner`.

  * OpenTuner depends on [SQLite](https://www.sqlite.org/index.html),
    which must also be installed.  SQLite can be found in the package
    system of virtually any Linux distribution.

  * Generating the graphs requires Numpy and
    [Matplotlib](https://matplotlib.org/) version 2 for Python, as
    well as a working LaTeX setup.

  * [bc](https://www.gnu.org/software/bc/) is needed for some of the
    data generation scripts.  This should be preinstalled (or easily
    installable) on just about any Unix system.

As a guideline, the `Dockerfile` contains commands showing how to
install the necessary components on a Debian/Ubuntu machine.

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

On some systems, depending on the OpenCL vendor, it may be necessary
to set some combination of the environment variables `LIBRARY_PATH`,
`CPATH`, and `LD_LIBRARY_PATH` for this to work.

You will need a relatively beefy GPU, as in particular LocVolCalib is
memory-hungry when being auto-tuned.  4GiB should be enough.

While Futhark-generated code can handle multiple available OpenCL
platforms, most of the third party benchmark implementations look only
at the first platform.  These may fail if the device name indicated in
`config.mk` is not part of the first platform.  On most systems, this
will not be an issue, but it may be worth looking at the contents of
`/etc/OpenCL/vendors`, or using the [clinfo] tool, which is available
in many package systems.

[clinfo]: https://github.com/Oblomov/clinfo

While Futhark code can compile and run correctly on macOS, it is our
experience that many Rodinia benchmarks cannot.  Furthermore, most
macOS systems do not have GPUs with enough memory available to run the
larger benchmarks.

The `python` executable on the default PATH must be Python 2, because
OpenTuner does not support Python 3.  For generating the graphs, you
will need Python with Matplotlib 2, Numpy, as well as a standard
working LaTeX setup.

For building the Futhark compiler you will need [stack], a build
tool for Haskell.  You can possibly also install a binary release of
Futhark, and modify `config.mk` to use that instead.  However, a
future (or past) release Futhark may not match the one this benchmark
suite was designed for.

[stack]: https://docs.haskellstack.org

You will also need [OpenTuner] installed.  This is usually
accomplished simply by running

    pip install --user opentuner

[OpenTuner]: http://opentuner.org/

## Technical details

The Makefile will automatically detect whether the matrix
multiplication experiment should use cuBLAS as the reference, or a
portable OpenCL implementation.  This is done by checking whether
`nvcc` in scope.  If this heuristic goes wrong, or cuBLAS is for some
reason not available, you can modify `config.mk` to set
`USE_CUBLAS=0`.  On machines without an NVIDIA GPU, the absence of
`nvcc` means that the OpenCL implementation gets picked.

## Other `make` targets

In case not the entire suite is able to execute on a given system,
there are some useful sub-targets that can be used to run just parts.
In particular, this can be used to obtain results on GPUs that do not
have enough memory to run the larger benchmarks.

### Plotting targets

  * `make matmul-runtimes-large.pdf` and `make
    matmul-runtimes-small.pdf`: run the matrix multiplication
    benchmark and plot the results.

  * `make LocVolCalib-runtimes.pdf`: run the LocVolCalib benchmark and
    plot the results.

  * `make bulk-impact-speedup.pdf`: run both Futhark and reference
    versions of the various Rodinia and Parboil benchmarks and plot
    the results.  This is perhaps the one most likely to fail, as it
    involves a significant amount of third party code, not all of
    which was designed with benchmarking and portability in mind.

### Results without plots

This can be useful if you are on a system that does not have an
appropriate version of Matplotlib installed.  The runtimes will be
printed on the screen, and the raw data also available in JSON format
in the `results` directory.  Runtimes are not computed; only the raw
execution time.

  * `make matmul-runtimes-large` and `make matmul-runtimes-small`: run
    the matrix multiplication benchmark.

  * `make LocVolCalib-runtimes`: run the LocVolCalib benchmark.

  * `make bulk-impact-speedup`: run both Futhark and reference
    versions of the various Rodinia and Parboil benchmarks.

### Very fine-grained targets

  * `make results/benchmark-moderate.json`: produce a JSON file with
    runtime results for *benchmark* compiled with moderate flattening,
    where *benchmark* must be one of `matmul`, `nn`, `pathfinder`,
    `nw`, `backprop`, `srad`, `lavaMD`, `OptionPricing`, `LocVolCalib`,
    or `heston32`.

 * `make results/benchmark-incremental.json`: as above, but with
   incremental flattening.

 * `make results/benchmark-incremental-tuned.json`: as above, but
   with incremental flattening and with auto-tuning.

 * `make results/benchmark-rodinia.json`: as above, but use the
   Rodinia implementation (*benchmark* may not be `matmul`,
   `heston32`, `OptionPricing` or `LocVolCalib`).

 * `make results/benchmark-finpar.json`: as above, but use the
   FinPar implementation (*benchmark* must be `OptionPricing` or
   `LocVolCalib`).

### Utility targets

  `make veryclean`: like `make clean`, but removes even the parts that have been
  downloaded externally.

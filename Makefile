include config.mk

ifeq ($(FUTHARK_OPENCL_DEVICE),)
  DEVICE_OPTION=
else
  DEVICE_OPTION=--pass-option=-d$(FUTHARK_OPENCL_DEVICE)
endif

RODINIA_RUNS=10

FUTHARK_BENCH_OPENCL_OPTIONS=--compiler=$(FUTHARK_OPENCL) $(DEVICE_OPTION)

ifeq ($(FUTHARK_OPENCL),bin/futhark-opencl)
  FUTHARK_OPENCL_DEPS=bin/futhark-opencl
endif

ifeq ($(FUTHARK_C),bin/futhark-c)
  FUTHARK_C_DEPS=bin/futhark-c
endif

ifeq ($(FUTHARK_DATASET),bin/futhark-dataset)
  FUTHARK_DATASET_DEPS=bin/futhark-dataset
endif

ifeq ($(FUTHARK_BENCH),bin/futhark-bench)
  FUTHARK_BENCH_DEPS=bin/futhark-bench
endif

FUTHARK_DEPS=$(FUTHARK_OPENCL_DEPS) $(FUTHARK_C_DEPS) $(FUTHARK_DATASET_DEPS) $(FUTHARK_BENCH_DEPS)

FUTHARK_AUTOTUNE=futhark/tools/futhark-autotune --futhark-bench=$(FUTHARK_BENCH) $(FUTHARK_BENCH_OPENCL_OPTIONS) --stop-after $(AUTOTUNE_SECONDS) --test-limit 10000000 --bail-threshold=5000

.PHONY: all benchmark clean veryclean
.SUFFIXES:
.SECONDARY:

all: $(FUTHARK_DEPS) rodinia_3.1-patched plots

plots: matmul-runtimes-large.pdf matmul-runtimes-small.pdf LocVolCalib-runtimes.pdf bulk-impact-speedup.pdf

.PHONY: matmul-runtimes-large matmul-runtimes-small
matmul-runtimes-large: results/matmul-moderate.json results/matmul-incremental.json results/matmul-incremental-tuned.json results/matmul-reference.json tools/matmul-plot.py
matmul-runtimes-small: results/matmul-moderate.json results/matmul-incremental.json results/matmul-incremental-tuned.json results/matmul-reference.json tools/matmul-plot.py

matmul-runtimes-large.pdf matmul-runtimes-large.tex: matmul-runtimes-large tools/matmul-plot.py
	python tools/matmul-plot.py $(MATMUL_REFERENCE) matmul-runtimes-large.pdf matmul-runtimes-large.tex $(MATMUL_SIZES_LARGE)


matmul-runtimes-small.pdf matmul-runtimes-small.tex: matmul-runtimes-small tools/matmul-plot.py
	python tools/matmul-plot.py $(MATMUL_REFERENCE) matmul-runtimes-small.pdf matmul-runtimes-small.tex $(MATMUL_SIZES_SMALL)

# General rules for running the simple cases of benchmarks.
results/%-moderate.json: benchmarks/%.fut benchmarks/%-data $(FUTHARK_DEPS)
	mkdir -p results
	$(FUTHARK_BENCH) $(FUTHARK_BENCH_OPENCL_OPTIONS) benchmarks/$*.fut --json $@
results/%-baseline.json: benchmarks/%.fut benchmarks/%-data $(FUTHARK_DEPS)
	mkdir -p results
	$(FUTHARK_BENCH) $(FUTHARK_BENCH_OPENCL_OPTIONS) benchmarks/$*-baseline.fut --json $@
results/%-incremental.json: benchmarks/%.fut benchmarks/%-data $(FUTHARK_DEPS)
	mkdir -p results
	FUTHARK_INCREMENTAL_FLATTENING=1 $(FUTHARK_BENCH) $(FUTHARK_BENCH_OPENCL_OPTIONS) benchmarks/$*.fut --json $@
results/%-incremental-tuned.json: benchmarks/%.fut benchmarks/%-data futhark $(FUTHARK_DEPS)
	mkdir -p results tunings
	FUTHARK_INCREMENTAL_FLATTENING=1 $(FUTHARK_AUTOTUNE) benchmarks/$*.fut --save-json tunings/$*.json
	FUTHARK_INCREMENTAL_FLATTENING=1 $(FUTHARK_BENCH) $(FUTHARK_BENCH_OPENCL_OPTIONS) benchmarks/$*.fut --json $@ $$(python tools/tuning_json_to_options.py < tunings/$*.json)

# You will also have to modify the data set stanzas in
# benchmarks/matmul.fut if you change these.
MATMUL_SIZES_LARGE=0 10 25
MATMUL_SIZES_SMALL=0 10 20

benchmarks/matmul-data: $(FUTHARK_DEPS)
	mkdir -p $@
	touch $@
	tools/make_matmul_matrices.sh $(MATMUL_SIZES_LARGE)
	tools/make_matmul_matrices.sh $(MATMUL_SIZES_SMALL)

ifeq ($(USE_CUBLAS),1)
reference/matmul/matmul: reference/matmul/matmul-cublas.cu
	$(NVCC) $< -o $@ -lcublas
MATMUL_REFERENCE=cuBLAS
else
reference/matmul/matmul: reference/matmul/matmul.c
	$(CC) $< -o $@ $(CFLAGS)
MATMUL_REFERENCE=hand-written
endif

results/matmul-reference.json: reference/matmul/matmul
	mkdir -p results
	(cd reference/matmul; ./matmul ../../$@ $(MATMUL_SIZES_LARGE) $(MATMUL_SIZES_SMALL)) || rm $@

benchmarks/pathfinder-data: $(FUTHARK_DEPS)
	mkdir -p $@
	touch $@
	$(FUTHARK_DATASET) -b -g [1][50][50000]i32 > $@/train-D1.in
	$(FUTHARK_DATASET) -b -g [300][100][192]i32 > $@/train-D2.in
	$(FUTHARK_DATASET) -b -g [1][100][100096]i32 > $@/D1.in
	$(FUTHARK_C) benchmarks/pathfinder.fut
	benchmarks/pathfinder -b < $@/D1.in > $@/D1.out
	$(FUTHARK_DATASET) -b -g [391][100][256]i32 > $@/D2.in
	$(FUTHARK_C) benchmarks/pathfinder.fut
	benchmarks/pathfinder -b < $@/D2.in > $@/D2.out

.PHONY: LocVolCalib-runtimes
LocVolCalib-runtimes: results/LocVolCalib-moderate.json results/LocVolCalib-incremental.json results/LocVolCalib-incremental-tuned.json results/LocVolCalib-finpar-AllParOpenCLMP.json results/LocVolCalib-finpar-OutParOpenCLMP.json

LocVolCalib-runtimes.pdf: LocVolCalib-runtimes tools/LocVolCalib-plot.py
	python tools/LocVolCalib-plot.py

results/LocVolCalib-finpar-%.json: results/LocVolCalib-%-small.raw results/LocVolCalib-%-medium.raw results/LocVolCalib-%-large.raw tools/LocVolCalib-json.py
	python tools/LocVolCalib-json.py $* > $@

results/LocVolCalib-AllParOpenCLMP-%.raw: bin/gpuid tools/run-finpar-bench.sh
	tools/run-finpar-bench.sh LocVolCalib/AllParOpenCLMP $* > $@ || (rm $@ && exit 1)

results/LocVolCalib-OutParOpenCLMP-%.raw: bin/gpuid tools/run-finpar-bench.sh
	tools/run-finpar-bench.sh LocVolCalib/OutParOpenCLMP $* > $@ || (rm $@ && exit 1)

results/OptionPricing-finpar.json: results/OptionPricing-finpar-D1.raw results/OptionPricing-finpar-D2.raw
	python tools/OptionPricing-json.py > $@ || (rm $@ && exit 1)

results/OptionPricing-finpar-D1.raw: bin/gpuid tools/run-finpar-bench.sh
	tools/run-finpar-OptionPricing.sh D1 > $@ || (rm $@ && exit 1)

results/OptionPricing-finpar-D2.raw: bin/gpuid tools/run-finpar-bench.sh
	tools/run-finpar-OptionPricing.sh D2 > $@ || (rm $@ && exit 1)

results/OptionPricing-finpar-%.raw: bin/gpuid tools/run-finpar-bench.sh
	tools/run-finpar-bench.sh OptionPricing/CppOpenCL $* > $@ || (rm $@ && exit 1)

## Tools.

bin/gpuid: tools/gpuid.c
	mkdir -p bin
	$(CC) -o $@ $< $(CFLAGS)

## Now for Rodinia scaffolding.  Crufty and hacky.

rodinia_3.1-patched: rodinia_3.1.tar.bz2
	@if ! md5sum --quiet -c rodinia_3.1.tar.bz2.md5; then \
          echo "Your rodinia_3.1.tar.bz2 has the wrong MD5-sum - delete it and try again."; exit 1; fi
	tar jxf rodinia_3.1.tar.bz2
	mv rodinia_3.1 rodinia_3.1-patched
	(cd $@; patch -p1 < ../rodinia_3.1-some-instrumentation.patch)

rodinia_3.1.tar.bz2:
	wget http://www.cs.virginia.edu/~kw5na/lava/Rodinia/Packages/Current/rodinia_3.1.tar.bz2

# This is a development rule that users should never use.
rodinia_3.1-some-instrumentation.patch: rodinia_3.1-patched
	diff -pur rodinia_3.1 rodinia_3.1-patched > $@ || true

# Skip the first measurement; we treat it as a warmup run.
results/%-rodinia.runtimes: bin/gpuid rodinia_3.1-patched
	mkdir -p results
	tools/rodinia_run.sh opencl/$* $(RODINIA_RUNS)
	tail -n +2 rodinia_3.1-patched/opencl/$*/runtimes > $@

## Bulk (impact) benchmarking

results/%-moderate.json: benchmarks/%-data $(FUTHARK_DEPS)
	mkdir -p results
	$(FUTHARK_BENCH) $(FUTHARK_BENCH_OPENCL_OPTIONS) benchmarks/$*.fut --json $@

results/%-incremental.json: benchmarks/%-data $(FUTHARK_DEPS)
	mkdir -p results
	FUTHARK_INCREMENTAL_FLATTENING=1 $(FUTHARK_BENCH) $(FUTHARK_BENCH_OPENCL_OPTIONS) benchmarks/$*.fut --json $@

tunings/%.json: benchmarks/%-data futhark $(FUTHARK_DEPS)
	mkdir -p tunings
	FUTHARK_INCREMENTAL_FLATTENING=1 $(FUTHARK_AUTOTUNE) benchmarks/$*.fut --save-json tunings/$*.json

results/%-incremental-tuned.json: tunings/%.json $(FUTHARK_DEPS)
	mkdir -p results
	FUTHARK_INCREMENTAL_FLATTENING=1 $(FUTHARK_BENCH) $(FUTHARK_BENCH_OPENCL_OPTIONS) benchmarks/$*.fut --json $@ $$(python tools/tuning_json_to_options.py < tunings/$*.json)

benchmarks/nn-data: $(FUTHARK_DEPS)
	mkdir -p $@
	touch $@
	N=1 M=700000 sh -c 'tools/nn-data.sh $(FUTHARK_DATASET) $$N $$M > $@/train-D1.in'
	N=2048 M=256 sh -c 'tools/nn-data.sh $(FUTHARK_DATASET) $$N $$M > $@/train-D2.in'
	N=1 M=855280 sh -c 'tools/nn-data.sh $(FUTHARK_DATASET) $$N $$M > $@/D1.in'
	N=4096 M=128 sh -c 'tools/nn-data.sh $(FUTHARK_DATASET) $$N $$M > $@/D2.in'

## Impact benchmarking

IMPACT_BENCHMARKS=benchmarks/nn.fut benchmarks/pathfinder.fut benchmarks/nw.fut benchmarks/backprop.fut benchmarks/srad.fut benchmarks/lavaMD.fut benchmarks/OptionPricing.fut benchmarks/heston32.fut
MODERATE_RESULTS=$(IMPACT_BENCHMARKS:benchmarks/%.fut=results/%-moderate.json)
INCREMENTAL_RESULTS=$(IMPACT_BENCHMARKS:benchmarks/%.fut=results/%-incremental.json)
AUTOTUNED_RESULTS=$(IMPACT_BENCHMARKS:benchmarks/%.fut=results/%-incremental-tuned.json)
BASELINE_RESULTS=results/srad-baseline.json results/backprop-baseline.json

IMPACT_RODINIA_BENCHMARKS_FULL=nw backprop lavaMD
IMPACT_RODINIA_BENCHMARKS_FULL_RESULTS=$(IMPACT_RODINIA_BENCHMARKS_FULL:%=results/%-rodinia.json)
IMPACT_RODINIA_BENCHMARKS_ONE=nn srad pathfinder
IMPACT_RODINIA_BENCHMARKS_ONE_RESULTS=$(IMPACT_RODINIA_BENCHMARKS_ONE:%=results/%-rodinia.json)

results/backprop-rodinia.json: rodinia_3.1-patched tools/rodinia_run.sh
	tools/rodinia_run.sh backprop D1 $(RODINIA_RUNS) > results/backprop-rodinia-D1.runtimes
	tools/rodinia_run.sh backprop D2 $(RODINIA_RUNS) > results/backprop-rodinia-D2.runtimes
	tools/raw_rodinia_to_json.py backprop D1 D2 > $@ || rm -f $@

results/nw-rodinia.json: rodinia_3.1-patched tools/rodinia_run.sh
	tools/rodinia_run.sh nw D1 $(RODINIA_RUNS) > results/nw-rodinia-D1.runtimes
	tools/rodinia_run.sh nw D2 $(RODINIA_RUNS) > results/nw-rodinia-D2.runtimes
	tools/raw_rodinia_to_json.py nw D1 D2 > $@ || rm -f $@

results/lavaMD-rodinia.json: rodinia_3.1-patched tools/rodinia_run.sh
	tools/rodinia_run.sh lavaMD D1 $(RODINIA_RUNS) > results/lavaMD-rodinia-D1.runtimes
	tools/rodinia_run.sh lavaMD D2 $(RODINIA_RUNS) > results/lavaMD-rodinia-D2.runtimes
	tools/raw_rodinia_to_json.py lavaMD D1 D2 > $@ || rm -f $@

results/nn-rodinia.json: rodinia_3.1-patched tools/rodinia_run.sh
	tools/rodinia_run.sh nn D1 $(RODINIA_RUNS) > results/nn-rodinia-D1.runtimes
	tools/raw_rodinia_to_json.py nn D1 > $@ || rm -f $@

results/srad-rodinia.json: rodinia_3.1-patched tools/rodinia_run.sh
	tools/rodinia_run.sh srad D1 $(RODINIA_RUNS) > results/srad-rodinia-D1.runtimes
	tools/raw_rodinia_to_json.py srad D1 > $@ || rm -f $@

results/pathfinder-rodinia.json: rodinia_3.1-patched tools/rodinia_run.sh
	tools/rodinia_run.sh pathfinder D1 $(RODINIA_RUNS) > results/pathfinder-rodinia-D1.runtimes
	tools/raw_rodinia_to_json.py pathfinder D1 > $@ || rm -f $@

.PHONY: bulk-impact-speedup
bulk-impact-speedup: $(MODERATE_RESULTS) $(INCREMENTAL_RESULTS) $(AUTOTUNED_RESULTS) $(BASELINE_RESULTS) $(IMPACT_RODINIA_BENCHMARKS_ONE_RESULTS) $(IMPACT_RODINIA_BENCHMARKS_FULL_RESULTS) results/OptionPricing-finpar.json

bulk-impact-speedup.pdf: bulk-impact-speedup tools/bulk-impact-plot.py
	tools/bulk-impact-plot.py $@

## Building Futhark

bin/futhark-%:
	mkdir -p bin
	cd futhark && stack setup
	cd futhark && stack build
	cp `cd futhark && stack exec which futhark-$*` $@

bin/futhark:
	mkdir -p bin
	cd futhark && stack setup
	cd futhark && stack build
	cp `cd futhark && stack exec which futhark` $@

## Artifact preparation
#
# The 'artifact' target predownloads everything such that the
# resulting artifact/image can be used without any Internet connection
# (and is thus fully reproducible).  This also builds the Futhark
# compiler, because the Haskell build tool ('stack') goes online to
# look for the library dependencies.

.PHONY: artifact
artifact: $(FUTHARK_DEPS) rodinia_3.1.tar.bz2

clean:
	rm -rf bin benchmarks/*.expected benchmarks/*.actual benchmarks/*-c benchmarks/matmul-data benchmarks/pathfinder-data benchmarks/nn-data tunings results *.pdf finpar.log

veryclean: clean
	rm -rf  rodinia_3.1-patched *.tgz *.tar.gz futhark finpar

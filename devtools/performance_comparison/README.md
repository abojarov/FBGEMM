# Performance comparison between two commits

In this folder there are scripts for comparison of two different commits for the FBGEMM repo. The scipts
contain complete automatic build and run of benchmarks. Build and run are performed from separate docker
containters.

## Build and run complete procedure

We will use the default setup for folders and folder names. This can be changed by setting different 
arguments for the `build_and_run.sh` script. All possible options are printed by calling `./build_and_run.sh --help`.

### Setting up the repos

First we clone the repo in the folder `~/work` and copy it in two places after which we checkout to two 
different commits. For this purpose we will use the `09132024_upstream_main` and `lii/recover_performance` 
branches and the coresponding folders `FBGEMM_main` and `FBGEMM_liirecperf`.

```
mkdir ~/work
cd ~/work
git clone --recursive -b 09132024_upstream_main git@github.com:abojarov/FBGEMM.git FBGEMM_main
git clone --recursive -b lii/recover-performance git@github.com:abojarov/FBGEMM.git FBGEMM_liirecperf
```

### Benchmarks folder

Next we create a folder for saving benchmark results (the default is `~/work/benchmarks`) and copy the
scripts to this folder. This is the folder from where we will run our builds and benchmarks.

```
mkdir ~/work/benchmarks
cp -r ~/work/FBGEMM_main/devtools/performance_comparison/* ~/work/benchmarks
cd ~/work/benchmarks
```

### Building and running benchmarks

Since the building and running of benchmarks is performed from docker containers, we first must 
assure that the containers don't exist. The default names of the containers are `$USER_FBGEMM_main` 
and `$USER_FBGEMM_liirecperf`. We run the build and run script:

```
./build_and_run.sh --folderA FBGEMM_main --folderB FBGEMM_liirecperf --buildA true --buildB true --runA true --runB true --createA true
```

or you can run the script in background and redirect output to a file `run.out`. When running in background you can leave the session and come back later.

```
nohup 2>&1 ./build_and_run.sh --folderA FBGEMM_main --folderB FBGEMM_liirecperf --buildA true --buildB true --runA true --runB true --createA true > run.out &
```

This call will:

1. Stop and remove a docker container with `$USER_FBGEMM_main`.
2. Run a docker container with name `$USER_FBGEMM_main`.
3. Build all the required libraries for FBGEMM.
4. Then it cds into mounted volume `~/work/FBGEMM_main/fbgemm_gpu` and builds the repo.
5. Create new folder structure for benchmarks.
5. Run benchmarks for `~/work/FBGEMM_main`.
6. Stop and remove a docker container with `$USER_FBGEMM_liirecperf`.
7. Run a docker container with name `$USER_FBGEMM_liirecperf`.
8. Build all the required libraries for FBGEMM.
9. Then it cds into mounted volume `~/work/FBGEMM_liirecperf/fbgemm_gpu` and builds the repo.
10. Run benchmarks for `~/work/FBGEMM_main` and appends data to the last created benchmark folder.

You can use the same script to rerun benchmarks (if you don't want the libs to be rebuilded):

```
./build_and_run.sh --folderA FBGEMM_main --folderB FBGEMM_liirecperf --runA true --runB true --createA true
```

or just build the libs wihout running

```
./build_and_run.sh --folderA FBGEMM_main --folderB FBGEMM_liirecperf --buildA true --buildB true
```

or any other combination of actions.

## Benchmark results

Running the script `run_benchmarks.sh` will automatically create folder of the name `benchmark_nn`
where `nn` is the next number in succession. If the user runs the script without creating new folder 
(`createA false` and `createB false` which is by default) then the benchmark results will be appended
on the last `benchmark_nn` folder.

After finishing, the results are saved in `benchmark_nn/bench_results.log`. Processing this data is
performed by running the python script (ex. for `benchmark_00`):

```
python3 parse_benchmarks.py ~/work/benchmarks/benchmark_00
```

and the output is located in the folder `benchmark_00`.
#!/bin/bash
#
# Script is to be run with the following arguments:
#     $1: -b username FBGEMM_name hipify_branch
#     $2: -r username FBGEMM_name create_dir
#
# Example:
#     docker exec -i -w /work/benchmarks abojarov_upstream bash -c "./run_benchmarks.sh true ../FBGEMM_main/fbgemm_gpu"
#     docker exec -i -w /work/benchmarks abojarov_liirecperf bash -c "./run_benchmarks.sh false ../FBGEMM_liirecperf/fbgemm_gpu"

print_usage() {
  printf "
  Script for running build and benchmarks for two different commits of FBGEMM library.

  Syntax: build_and_run.sh --folderA folder_name --folderB folder_name [--username uname] [--basefolder folder_name] [--benchfd folder_name] [--hipifyA commit] [--hipifyB commit] [--createA false] [--createB false] [--buildA false] [--buildB false]  [--runA false] [--runB false]
  
  options:
  --folderA folder_name    : Folder where the A repo resides (required)
  --folderB folder_name    : Folder where the B repo resides (required)
  --username uname         : Username where the home folder is located (default is the \$USER env. variable)
  --basefolder folder_name : Base folder where the repos A and B reside (default is 'work')
  --benchfd folder_name  : Name of the benchmark folder (inside the basefolder default is 'benchmarks')
  --hipifyA commit       : Name of the hipify submodule commit to checkout repo A to (default is 'master')
  --hipifyB commit       : Name of the hipify submodule commit to checkout repo B to (default is 'master')
  --createA bool         : Should new folder structure be created before running of the benchmark for repo A (true/false, default is false)
  --createB bool         : Should new folder structure be created before running of the benchmark for repo B (true/false, default is false)
  --buildA bool          : Should new build of repo A be performed (true/false, default is false)
  --buildB bool          : Should new build of repo B be performed (true/false, default is false)
  --runA bool            : Should run of benchmark from repo A be performed (true/false, default is false)
  --runB bool            : Should run of benchmark from repo B be performed (true/false, default is false)
  -h, --help             : Print this message and exit
"
}

UNAME=${USER}
BASEFD=work
BENCHFD=benchmarks
HCA=master
HCB=master
CA=false
CB=false
BLDA=false
BLDB=false
RUNA=false
RUNB=false

while [ $# -gt 0 ]
do
    case $1 in
    --username) UNAME="$2" ;;
    --basefolder) BASEFD="$2" ;;
    --benchfd) BENCHFD="$2" ;;
    --folderA) FDA="$2" ;;
    --folderB) FDB="$2" ;;
    --hipifyA) HCA="$2" ;;
    --hipifyB) HCB="$2" ;;
    --createA) CA="$2" ;;
    --createB) CB="$2" ;;
    --buildA) BLDA="$2" ;;
    --buildB) BLDB="$2" ;;
    --runA) RUNA="$2" ;;
    --runB) RUNB="$2" ;;
    -h|--help) print_usage && exit 1;;
    esac
    shift
done

echo "username:              ${UNAME}"
echo "base folder:           ${BASEFD}"
echo "benchmarks folder:     ${BENCHFD}"
echo "folder name A:         ${FDA}"
echo "folder name B:         ${FDB}"
echo "hipify commit A:       ${HCA}"
echo "hipify commit B:       ${HCB}"
echo "create bench folder A: ${CA}"
echo "create bench folder B: ${CB}"
echo "build A:               ${BLDA}"
echo "build B:               ${BLDB}"
echo "run A:                 ${RUNA}"
echo "run B:                 ${RUNB}"

if [ -z "$FDA" ]; then
    echo "Error: Folder A is not given, exiting!"
    exit 1
fi

if [ -z "$FDB" ]; then
    echo "Error: Folder B is not given, exiting!"
    exit 1
fi

# Functions are to be run with three arguments:
#     $1: Username
#     $2: Name of the folder where FBGEMM is located
#     $3: Commit for the hipify_torch
build_docker() {
    UNAME=$1
    FBGEMM_COMMIT=$2
    HIPIFY_TORCH_COMMIT=$3
    DOCK_NAME=${UNAME}_${FBGEMM_COMMIT}

    echo ">>>>>>> RUN $DOCK_NAME"

    docker stop $DOCK_NAME && docker rm $DOCK_NAME

    docker run -d -t -i --name $DOCK_NAME -v /home/$UNAME/$BASEFD:/work --network=host --shm-size 16G --device=/dev/kfd --device=/dev/dri --group-add video --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --ipc=host rocm/pytorch:latest bash

    docker exec -i $DOCK_NAME bash -c "pip3 uninstall -y torch"

    docker exec -i $DOCK_NAME bash -c "pip3 install --pre torch==2.5.0 --index-url https://download.pytorch.org/whl/test/rocm6.2"

    docker exec -i $DOCK_NAME bash -c "git config --global --add safe.directory /work/$FBGEMM_COMMIT && git config --global --add safe.directory /work/$FBGEMM_COMMIT/third_party/hipify_torch"

    docker exec -i $DOCK_NAME bash -c "cd /work/$FBGEMM_COMMIT/third_party/hipify_torch && git checkout $HIPIFY_TORCH_COMMIT"

    docker exec -i -w /work/$FBGEMM_COMMIT/fbgemm_gpu $DOCK_NAME bash -c "pip3 install -r requirements.txt"

    docker exec -i -w /work/$FBGEMM_COMMIT/fbgemm_gpu $DOCK_NAME bash -c "rm -rf ./_skbuild"

    docker exec -i -w /work/$FBGEMM_COMMIT/fbgemm_gpu $DOCK_NAME bash -c "export MAX_JOBS='nproc' && export PYTORCH_ROCM_ARCH=gfx90a:xnack- && git clean -dfx && python setup.py -DHIP_ROOT_DIR=/opt/rocm -DCMAKE_C_FLAGS="-DTORCH_USE_HIP_DSA" -DCMAKE_CXX_FLAGS="-DTORCH_USE_HIP_DSA" build develop 2>&1 | tee build.log"
}

# Functions are to be run with three arguments:
#     $1: Username
#     $2: Name of the folder where FBGEMM is located
#     $3: Should benchmark create new folder
run_benchmark_docker() {
    UNAME=$1
    FBGEMM_COMMIT=$2
    CREATE_BENCH_DIR=$3
    DOCK_NAME=${UNAME}_${FBGEMM_COMMIT}

    docker exec -i -w /work/$BENCHFD $DOCK_NAME bash -c "./run_benchmarks.sh ../$FBGEMM_COMMIT/fbgemm_gpu $CREATE_BENCH_DIR"

}

if $BLDA; then
    build_docker $UNAME $FDA $HCA
fi
if $RUNA; then
    run_benchmark_docker $UNAME $FDA $CA
fi
if $BLDB; then
    build_docker $UNAME $FDB $HCB
fi
if $RUNB; then
    run_benchmark_docker $UNAME $FDB $CB
fi
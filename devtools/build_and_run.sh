#!/bin/bash

# Functions are to be run with three arguments:
#     $1: Username
#     $2: Name of the folder where FBGEMM is located (ex. for FBGEMM_commit01 the value is commit01)
#     $3: Commit for the hipify_torch
build_docker() {
    UNAME=$1
    FBGEMM_COMMIT=$2
    HIPIFY_TORCH_COMMIT=$3
    DOCK_NAME=${UNAME}_${FBGEMM_COMMIT}

    echo ">>>>>>> RUN $DOCK_NAME"

    docker run -d -t -i --name $DOCK_NAME -v /home/$UNAME/work:/work --network=host --shm-size 16G --device=/dev/kfd --device=/dev/dri --group-add video --cap-add=SYS_PTRACE --security-opt seccomp=unconfined --ipc=host rocm/pytorch:latest bash

    docker exec -i $DOCK_NAME bash -c "pip3 uninstall -y torch"

    docker exec -i $DOCK_NAME bash -c "pip3 install --pre torch==2.5.0 --index-url https://download.pytorch.org/whl/test/rocm6.2"

    docker exec -i $DOCK_NAME bash -c "git config --global --add safe.directory /work/FBGEMM_$FBGEMM_COMMIT && git config --global --add safe.directory /work/FBGEMM_$FBGEMM_COMMIT/third_party/hipify_torch"

    docker exec -i $DOCK_NAME bash -c "cd /work/FBGEMM_$FBGEMM_COMMIT/third_party/hipify_torch && git checkout $HIPIFY_TORCH_COMMIT"

    docker exec -i -w /work/FBGEMM_$FBGEMM_COMMIT/fbgemm_gpu $DOCK_NAME bash -c "pip3 install -r requirements.txt"

    docker exec -i -w /work/FBGEMM_$FBGEMM_COMMIT/fbgemm_gpu $DOCK_NAME bash -c "rm -rf ./_skbuild"

    docker exec -i -w /work/FBGEMM_$FBGEMM_COMMIT/fbgemm_gpu $DOCK_NAME bash -c "export MAX_JOBS='nproc' && export PYTORCH_ROCM_ARCH=gfx90a:xnack- && git clean -dfx && python setup.py -DHIP_ROOT_DIR=/opt/rocm -DCMAKE_C_FLAGS="-DTORCH_USE_HIP_DSA" -DCMAKE_CXX_FLAGS="-DTORCH_USE_HIP_DSA" build develop 2>&1 | tee build.log"
}

# Functions are to be run with three arguments:
#     $1: Username
#     $2: Name of the folder where FBGEMM is located (ex. for FBGEMM_commit01 the value is commit01)
#     $3: Should benchmark create new folder
run_benchmark_docker() {
    UNAME=$1
    FBGEMM_COMMIT=$2
    CREATE_BENCH_DIR=$3
    DOCK_NAME=${UNAME}_${FBGEMM_COMMIT}

    docker exec -i -w /work/benchmarks $DOCK_NAME bash -c "./run_benchmarks.sh ../FBGEMM_$FBGEMM_COMMIT/fbgemm_gpu $CREATE_BENCH_DIR"

}

# build_docker abojarov main master
run_benchmark_docker abojarov main true

# build_docker abojarov liirecperf master
run_benchmark_docker abojarov liirecperf false
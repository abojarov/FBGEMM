#!/bin/bash
#
# Script is to be run with two arguments:
#     $1: Folder from where the benchmark is to be run
#     $2: Should a new folder be created
#
# Example:
#     docker exec -i -w /work/benchmarks abojarov_upstream bash -c "./run_benchmarks.sh true ../FBGEMM_main/fbgemm_gpu"
#     docker exec -i -w /work/benchmarks abojarov_liirecperf bash -c "./run_benchmarks.sh false ../FBGEMM_liirecperf/fbgemm_gpu"

# User defined variables
BASE_LOGFILE=run_benchmarks.log
BASE_LOGFILE_RESULTS=bench_results.log

OUT_BASE_FD=./benchmark_

# Start with the first number
OUT_BASE_FD_CNT=0

# Construct the initial folder name
OUT_FD="${OUT_BASE_FD}$(printf "%02d" $OUT_BASE_FD_CNT)"

set_folder() {
    if $1; then
        echo ">>>>>>> Create new output folder"
        # Loop until a folder with the constructed name exists
        while [ -d "$OUT_FD" ]; do
            # Increment the counter
            OUT_BASE_FD_CNT=$((OUT_BASE_FD_CNT + 1))
            # Construct the new folder name
            OUT_FD="${OUT_BASE_FD}$(printf "%02d" $OUT_BASE_FD_CNT)"
        done

        # Create the directory
        mkdir "$OUT_FD"

        touch $LOGFILE
        touch $LOGFILE_RESULTS
    else
        echo ">>>>>>> Append to output folder"
        # Loop until a folder with the constructed name exists
        while [ -d "$OUT_FD" ]; do
            # Increment the counter
            OUT_BASE_FD_CNT=$((OUT_BASE_FD_CNT + 1))
            # Construct the new folder name
            OUT_FD="${OUT_BASE_FD}$(printf "%02d" $OUT_BASE_FD_CNT)"
        done

        OUT_FD="${OUT_BASE_FD}$(printf "%02d" $((OUT_BASE_FD_CNT - 1)))"
    fi

    LOGFILE="${OUT_FD}/${BASE_LOGFILE}"
    LOGFILE_RESULTS="${OUT_FD}/${BASE_LOGFILE_RESULTS}"
    echo ">>>>>>> Output folder    : $OUT_FD"
    echo ">>>>>>> Log file         : $LOGFILE"
    echo ">>>>>>> Results log file : $LOGFILE_RESULTS"

    echo ">>>>>>> Running run_benchmarks.sh" >> $LOGFILE
    echo ">>>>>>> Running run_benchmarks.sh" >> $LOGFILE_RESULTS
    
    # Change owner since this is run from a docker container
    chown --reference=./ -R ./*
}

run_benchmarks() {
    exec >> $LOGFILE_RESULTS
    exec 2>&1
    pushd $1
    echo ">>>>>>> Call to run_benchmarks with : $1"
    echo ">>>>>>> Current HEAD       : `git rev-parse --abbrev-ref HEAD`"
    echo ">>>>>>> Current commit SHA : `git rev-parse --verify HEAD`"
    for alpha in 1.0 1.15; do  
        for output_t in fp16 fp32; do  
            for emb_dim in 128 160; do  
                for bag_size in 8 40; do  
                    echo ">>>>>>> Parameters set: alpha=$alpha, output_t=$output_t, emb_dim=$emb_dim, bag_size=$bag_size"
                    CMD="python bench/split_table_batched_embeddings_benchmark.py device --alpha $alpha --bag-size $bag_size --batch-size 131072 --embedding-dim $emb_dim --weights-precision fp16 --num-embeddings 7000000 --num-tables 2 --output-dtype $output_t --iters 100 --warmup-runs 10 --flush-gpu-cache-size-mb 80 --return-vectors True --output-dtype fp32"
                    echo ">>>>>>> Command: $CMD"
                    `$CMD`
                done  
            done  
        done  
    done
    chown --reference=./ -R ./*
    popd
}

echo ">>>>>>> CREATE_NEW_FOLDER: $1"
echo ">>>>>>>   RUN_FROM_FOLDER: $2"

set_folder $2
run_benchmarks $1

#!/bin/bash

mkdir -p evaluation_ad

run_anomaly_detection() {
    local method=$1
    local dataset=$2
    local penalty=$3
    local simple_flag=$4

    if [ -z "$penalty" ]; then
        if [ "$simple_flag" == "simple" ]; then
            file_path="./evaluation_ad/${method}_${dataset}_simple.txt"
        else
            file_path="./evaluation_ad/${method}_${dataset}_full.txt"
        fi
    else
        if [ "$simple_flag" == "simple" ]; then
            file_path="./evaluation_ad/${method}_${penalty}_${dataset}_simple.txt"
        else
            file_path="./evaluation_ad/${method}_${penalty}_${dataset}_full.txt"
        fi
    fi

    if [ -f "$file_path" ]; then
        echo "$file_path already exists, skipping."
    else
        if [ -z "$penalty" ]; then
            python anomaly_detection.py --method $method --dataset $dataset $([ "$simple_flag" == "simple" ] && echo "--simple") > "$file_path"
        else
            python anomaly_detection.py --method $method --penalty $penalty --dataset $dataset $([ "$simple_flag" == "simple" ] && echo "--simple") > "$file_path"
        fi
    fi
}

echo "N-Sigma"

for dataset in sock-shop online-boutique train-ticket; do
    run_anomaly_detection nsigma $dataset "" simple
    run_anomaly_detection nsigma $dataset "" full
done

echo "BOCPD"

for dataset in sock-shop online-boutique train-ticket; do
    run_anomaly_detection bocpd $dataset "" simple
    run_anomaly_detection bocpd $dataset "" full
done
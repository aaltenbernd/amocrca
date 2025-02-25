#!/bin/bash

mkdir -p evaluation_rca

run_analysis() {
    local rca=$1
    local ad=$2

    if [ -n "$ad" ]; then
        file_path="./evaluation_rca/${rca}_${ad}.txt"
        echo "$rca ($ad)"
    else
        if [ "$rca" == "ours" ]; then
            file_path="./evaluation_rca/amocrca.txt"
            echo "amocrca"
        else
            file_path="./evaluation_rca/${rca}.txt"
            echo "$rca"
        fi
    fi
    
    if [ -e "$file_path" ]; then
        echo "$file_path already exists, skipping."
    else
        command="python root_cause_analysis.py --rca $rca"
        if [ -n "$ad" ]; then
            command="$command --ad $ad"
        else
            if [ "$rca" == "ours" ]; then
                command="$command --amoc"
            fi
        fi
        if [ "$rca" == "ours" ]; then
            command="$command --rcr --lma"
        fi
        echo $command
        $command > $file_path
    fi
}

# AmocRCA

rca=ours

run_analysis $rca inject
run_analysis $rca nsigma
run_analysis $rca bocpd
run_analysis $rca

# N-Sigma

rca=nsigma

run_analysis $rca inject
run_analysis $rca nsigma
run_analysis $rca bocpd

# BARO

rca=baro

run_analysis $rca inject
run_analysis $rca nsigma
run_analysis $rca bocpd
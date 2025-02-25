# AmocRCA

AmocRCA is a highly effective and efficient approach to Root Cause Analysis (RCA) using metric data only that is based on a recent and promising approach for RCA named BARO. It leverages At Most One Change (AMOC) segmentation to make the scoring mechanism independent of anomaly detection, and employs a relative correlation ranking that enhances the scoring mechanism while reducing the need for a preselected set of metrics.

## Prerequisites

* unzip
* wget
* python

## Installation

```
python -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

## Datasets

```
./download_data.sh
```

## Usage

```
python ./root_cause_analysis.py --rcr --lma --amoc
```

## Reproduce RQ1 and RQ2

```
./anomaly_detection.sh
```

or 

```
unzip evaluation_ad.zip
```

then

```
./root_cause_analysis.sh
```

Results can be found in `evaluation_rca`

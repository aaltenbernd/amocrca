# AmocRCA

In this paper, we present AmocRCA, a highly effective and efficient approach to Root Cause Analysis (RCA) using metric data only. A fast and reliable localization of root causes is decisive for self-stabilization of large systems in production and thus for continuous operation. Unlike many multi-modal approaches, we omit the necessity to create and maintain topology and interaction graphs as well as to collect and interpret semantically rich data such as logs and traces for the sake of quick localization/reaction and low computational overhead while achieving comparable results in terms of RCA precision. AmocRCA is based on a recent and promising approach for RCA named BARO. It leverages At Most One Change (AMOC) segmentation to make the scoring mechanism independent of anomaly detection, and employs a relative correlation ranking that enhances the scoring mechanism while reducing the need for a preselected set of metrics. The experimental results confirm the improvement in terms of effectiveness, while achieving comparable efficiency. The latter is an important requirement for deploying the method in productive large-scale, data-intensive applications, where fault localization has a limited time constraint.

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

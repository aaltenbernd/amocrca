import glob
import argparse
import numpy as np

from functools import partial
from tqdm import tqdm
from time import time

from utils import prepare_data
from bocpd import multivariate_bocpd


def nsigma(data, k=3, startsfrom=100):
    anomalies = []
    for col in data.columns:
        for i in range(startsfrom, len(data)):
            mean = data[col].iloc[:i].mean()
            std = data[col].iloc[:i].std()            
            if abs(data[col].iloc[i] - mean) > k * std:
                anomalies.append(i)
    anomalies.append(len(data))
    return anomalies


def bocpd(data):
    anomalies = multivariate_bocpd(data)
    return anomalies


def run(datapaths, args):
    results = []
    tp = tn = fp = fn = 0
    total_runtime = 0
    for datapath in tqdm(datapaths, desc="Running"):
        data, data_scaled, inject_time = prepare_data(datapath=datapath)

        latency_keys = ["latency-50", "lat_50", "latency", "lat"]
        latency_cols = next(([x for x in data.columns if key in x] for key in latency_keys if any(key in x for x in data.columns)), [])

        error_keys = ["_error", "err"]
        error_cols = next(([x for x in data.columns if key in x] for key in error_keys if any(key in x for x in data.columns)), [])

        cols = latency_cols + error_cols

        data = data[cols]
        data_scaled = data_scaled[cols]

        anomaly_detection = globals()[args.method]
        if args.method == "amoc":
            anomaly_detection = partial(anomaly_detection, penalty=args.penalty)
        else:
            anomaly_detection = partial(anomaly_detection)

        start = time()
        anomalies = anomaly_detection(data=data_scaled)
        end = time()

        runtime = end-start
        total_runtime += runtime

        if len(anomalies) > 1:
            tp += 1
        else:
            fn += 1

        if anomalies[0] < inject_time:
            fp += 1
        else:
            tn += 1

        results.append([datapath, anomalies, f"{runtime:.2f}"])
        
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = 2 * precision * recall / (precision + recall)

    print(f"====== {args.method} ======")
    print(f"Precision : {precision:.2f}")
    print(f"Recall    : {recall:.2f}")
    print(f"F1        : {f1:.2f}")
    print(f"Time(Avg) : {total_runtime/len(datapaths):.2f}")
    print()

    for result in results:
        result = [str(x) for x in result]
        print(" ".join(result))


if __name__ == '__main__':    
    parser = argparse.ArgumentParser(description="Parse method and penalty options.")
    parser.add_argument("--method", type=str, required=True, help="Select the method to use. This argument is required.")
    parser.add_argument("--penalty", type=float, help="Select penalty (required if --method is 'amoc').")
    parser.add_argument("--dataset", type=str, required=True, help="Select dataset.")
    parser.add_argument("--simple", action='store_true', help="Select simple.")

    args = parser.parse_args()
    if args.method == "amoc" and args.penalty is None:
        parser.error("--penalty is required when --method is 'amoc'.")
    
    datasets = [                
        ("data/combined/sock-shop", "simple_data.csv", True),
        ("data/combined/online-boutique", "simple_data.csv", True),
        ("data/combined/train-ticket", "simple_data.csv", True),
        ("data/combined/sock-shop", "data.csv", False),
        ("data/combined/online-boutique", "data.csv", False),
        ("data/combined/train-ticket", "data.csv", False),
        ("data/combined", "*.csv", False)
    ]

    selected_dataset = None
    for dataset in datasets:
        if args.dataset in dataset[0] and args.simple == dataset[2]:
            selected_dataset = dataset

    if selected_dataset:
        datapaths = list(glob.glob(f"./{selected_dataset[0]}/**/{selected_dataset[1]}", recursive=True))
        run(datapaths, args=args)

import argparse
import re
import glob
import re
import os

from time import time
from functools import partial
from utils import prepare_data, to_services
from scoring import scoring
from tqdm import tqdm

from os.path import dirname, basename

MAXIMUM_RUNTIME = 7200


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=False, help="Select dataset")
    parser.add_argument("--simple", action='store_true', help="Select simple")
    
    # AD
    parser.add_argument("--ad", type=str, required=False, help="Select anomaly detection method")

    # RCA
    parser.add_argument('--rca', type=str, required=False, help="Select root cause analysis method")
    
    # AmocRCA Options:
    parser.add_argument("--amoc", action='store_true', help="Enable AMOC segmentation")
    parser.add_argument("--rcr", action='store_true', help="Enable relative correlation ranking")
    parser.add_argument("--lma", action='store_true', help="Enable leading metric alignment")
    
    args = parser.parse_args()
    
    print(f"-> Dataset: {args.dataset}")
    print(f"-> Simple: {args.simple}")
    print()
    print(f"-> AD Method: {args.ad}")
    print(f"-> RCA Method: {args.rca}")
    print()
    print(f"-> AmocRCA:")
    print(f"     AMOC Segmentation: {args.amoc}")
    print(f"     Relative Correlation Ranking: {args.rcr}")
    print(f"     Leading Metric Alignment: {args.lma}")

    return args


def run_rca(args, anomaly, data, data_scaled):
    scores = scoring(data=data, data_scaled=data_scaled, anomaly=anomaly, rca=args.rca, amoc=args.amoc, rcr=args.rcr, lma=args.lma)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_scores


def run_for_datapath(datapath, args):
    args.datapath = datapath

    data, data_scaled, inject_time = prepare_data(datapath=datapath)
        
    if args.ad is None or args.ad == "inject":
        anomaly = inject_time
    else:
        dataset = datapath.strip(os.sep).split(os.sep)[3]

        complexity = "simple" if "simple" in datapath else "full"
        anomalies_path = f"./evaluation_ad/{args.ad}_{dataset}_{complexity}.txt"

        anomalies = None
        with open(anomalies_path, "r") as file:
            for line in file:
                if args.datapath in line.lower():
                    anomalies = line.strip()
                    break
        
        anomalies = re.search(r'\[(.*?)\]', anomalies).groups()[0]
        anomaly = anomalies.split(",")[0]
        anomaly = int(anomaly)    
    
    rca_start = time()
    sorted_scores = run_rca(args, anomaly, data, data_scaled)
    rca_end = time()    

    return datapath, rca_end-rca_start, sorted_scores


def run(dataset, dataset_file, simple, args):
    datapaths = list(glob.glob(f"./{dataset}/**/{dataset_file}", recursive=True))

    func = partial(run_for_datapath, args=args)

    features = []

    for datapath in tqdm(datapaths, desc="Running"):
        start_time = time()
        features.append(func(datapath))
        elapsed_time = time() - start_time
        if elapsed_time > MAXIMUM_RUNTIME:
            return ['-'] * 7, ['-'] * 7

    row = evaluate(features=features)
    row_fg = evaluate_fg(features=features, simple=simple)
    return row, row_fg


def evaluate(features):
    precision = [{}, {}, {}, {}, {}]
    average = {}

    count_metric = {}
    metrics = ['cpu', 'mem', 'disk', 'delay', 'loss']

    rca_total_time = 0
    rca_avg_time = 0

    for feature in features:
        rca_total_time += feature[1]
        rca_avg_time += 1
        
        datapath = feature[0]
    
        sorted_scores = feature[2]
        ranks = [x[0] for x in sorted_scores]
        service_ranks = to_services(ranks)
        true_root_cause = basename(dirname(dirname(datapath)))

        service = true_root_cause.split("_")[0]
        metric = true_root_cause.split("_")[1]

        if service in service_ranks[:1]:
            precision[0][metric] = precision[0].get(metric, 0.0) + 1
        if service in service_ranks[:2]:
            precision[1][metric] = precision[1].get(metric, 0.0) + 1
        if service in service_ranks[:3]:
            precision[2][metric] = precision[2].get(metric, 0.0) + 1
        if service in service_ranks[:4]:
            precision[3][metric] = precision[3].get(metric, 0.0) + 1
        if service in service_ranks[:5]:
            precision[4][metric] = precision[4].get(metric, 0.0) + 1
        count_metric[metric] = count_metric.get(metric, 0.0) + 1

    rca_avg_time = rca_total_time / rca_avg_time if rca_avg_time > 0 else 0

    row = []

    for metric in metrics:
        if metric in count_metric:
            for p in precision:
                p[metric] = p.get(metric, 0.0) / count_metric[metric]
                average[metric] = average.get(metric, 0.0) + p[metric]
    
    count = 0
    overall_average = 0.0
    for metric in metrics:
        if metric in average:
            average[metric] = average[metric] / 5
            rounded = f"{round(average[metric], 2):.2f}"
            row.append(rounded)
            overall_average += average[metric]
            count += 1
        else:
            row.append("-")

    overall_average = overall_average / count if count > 0 else 0

    rounded = f"{round(overall_average, 2):.2f}"
    row.append(rounded)
    rounded = f"{round(rca_avg_time, 2):.2f}"
    row.append(rounded)

    return row


def evaluate_fg(features, simple):
    precision = [{}, {}, {}, {}, {}]
    average = {}

    count_metric = {}
    metrics = ['cpu', 'mem', 'disk', 'delay', 'loss']

    rca_total_time = 0
    rca_avg_time = 0

    for feature in features:
        rca_total_time += feature[1]
        rca_avg_time += 1
        
        datapath = feature[0]
    
        sorted_scores = feature[2]
        ranks = [x[0] for x in sorted_scores]
        # service_ranks = to_services(ranks)
        true_root_cause = basename(dirname(dirname(datapath)))

        service = true_root_cause.split("_")[0]
        metric = true_root_cause.split("_")[1]

        check_metric = metric
        if metric == 'delay':
            check_metric = 'lat'
        if metric == 'disk':
            check_metric = '-fs-'

        if metric == 'loss':
            check_metric = 'lat'
        if metric == 'disk' and simple:
            continue

        for i in range(1, 6):
            for rank in ranks[:i]:
                if service in rank and check_metric in rank:
                    precision[i-1][metric] = precision[i-1].get(metric, 0.0) + 1
                    break

        count_metric[metric] = count_metric.get(metric, 0.0) + 1

    rca_avg_time = rca_total_time / rca_avg_time if rca_avg_time > 0 else 0

    row = []

    for metric in metrics:
        if metric in count_metric:
            for p in precision:
                p[metric] = p.get(metric, 0.0) / count_metric[metric]
                average[metric] = average.get(metric, 0.0) + p[metric]

    count = 0
    overall_average = 0.0
    for metric in metrics:
        if metric in average:
            average[metric] = average[metric] / 5
            rounded = f"{round(average[metric], 2):.2f}"
            row.append(rounded)
            overall_average += average[metric]
            count += 1
        else:
            row.append("-")

    overall_average = overall_average / count if count > 0 else 0

    rounded = f"{round(overall_average, 2):.2f}"
    row.append(rounded)
    rounded = f"{round(rca_avg_time, 2):.2f}"
    row.append(rounded)

    return row


def run_for_datasets(args, datasets):
    avg_precision = []
    avg_precision_fg = []  
    avg_time_rca = [] 

    print()

    for dataset in datasets:
        print(dataset)
        row, row_fg = run(dataset=dataset[0], dataset_file=dataset[1], simple=dataset[2], args=args)
        print(row)
        print(row_fg)
        avg_precision.append(row[5])
        avg_precision_fg.append(row_fg[5])
        avg_time_rca.append(row[6])
        print()

    print()
    print("Average Precision:")
    print(' & '.join(avg_precision) + ' \\\\')

    print()
    print("Average Precision Fine-Grained:")
    print(' & '.join(avg_precision_fg) + ' \\\\')

    print()
    print("Average Time (RCA):")
    print(' & '.join(avg_time_rca) + ' \\\\')

    
if __name__ == '__main__':
    args = parse_args()

    datasets = [                
        ("data/combined/sock-shop", "simple_data.csv", True),
        ("data/combined/online-boutique", "simple_data.csv", True),
        ("data/combined/train-ticket", "simple_data.csv", True),
        ("data/combined/sock-shop", "data.csv", False),
        ("data/combined/online-boutique", "data.csv", False),
        ("data/combined/train-ticket", "data.csv", False)
    ]

    if args.dataset: 
        selected_dataset = None
        for dataset in datasets:
            if args.dataset in dataset[0] and args.simple == dataset[2]:
                selected_dataset = dataset

        if selected_dataset:
            datasets = [selected_dataset]
        else:
            datasets = []

    run_for_datasets(args, datasets=datasets)

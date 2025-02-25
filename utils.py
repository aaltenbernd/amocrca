import os
import pandas as pd

from sklearn.preprocessing import MinMaxScaler

def prepare_data(datapath):
    data = pd.read_csv(datapath)

    parent_path = os.path.dirname(datapath)

    with open(f"{parent_path}/inject_time.txt", 'r') as file:
        inject_time = file.read().strip()
        try:
            inject_time = int(inject_time)
        except ValueError:
            print("The inject.txt does not contain a valid integer.")

    inject_time = int(inject_time - data['time'][0])

    data = data.ffill()
    data = data.fillna(0)

    columns = data.columns[data.nunique() > 1]
    columns = [x for x in columns if "time" not in x]
    
    data = data[columns]

    x = data.values 
    min_max_scaler = MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    data_scaled = pd.DataFrame(x_scaled, columns=data.columns, index=data.index)

    return data, data_scaled, inject_time


def to_services(ranks):
    _service_ranks = [r.split("_")[0] for r in ranks]
    service_ranks = []
    for s in _service_ranks:
        if s not in service_ranks:
            service_ranks.append(s)
    return service_ranks

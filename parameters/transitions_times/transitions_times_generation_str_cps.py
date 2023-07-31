import json
import os

import np as np

np.random.seed(12345)
nb_scaling_sites = 15

min_value = 1
max_value = 30
mu, sigma = 0.7, 1.1  # mean and standard deviation
size = 1000
number_generator = np.random.lognormal(mu, sigma, size)
number_generator = iter(list(filter(lambda x: 1 <= x <= 30, number_generator)))

all_transitions_times = {"transitions_times": {}}
transitions_times = all_transitions_times["transitions_times"]
transitions_times["database"] = {
    "configure0": round(next(number_generator), 2),
    "configure1": round(next(number_generator), 2),
    "bootstrap": round(next(number_generator), 2),
    "deploy": round(next(number_generator), 2),
    "interrupt": round(next(number_generator), 2),
    "unconfigure": round(next(number_generator), 2),
}
transitions_times["system"] = {
    "initiate0": round(next(number_generator), 2),
    "initiate1": round(next(number_generator), 2),
    "initiate2": round(next(number_generator), 2),
    "deploy": round(next(number_generator), 2),
    "stop": round(next(number_generator), 2),
}
for i in range(nb_scaling_sites):
    transitions_times[f"listener{i}"] = {
        "start": round(next(number_generator), 2),
        "configure": round(next(number_generator), 2),
        "run": round(next(number_generator), 2),
        "interrupt": round(next(number_generator), 2),
    }
    transitions_times[f"sensor{i}"] = {
        "provision0": round(next(number_generator), 2),
        "provision1": round(next(number_generator), 2),
        "provision2": round(next(number_generator), 2),
        "install": round(next(number_generator), 2),
        "configure": round(next(number_generator), 2),
        "run": round(next(number_generator), 2),
        "pause": round(next(number_generator), 2),
    }

with open(f"{os.path.dirname(os.path.realpath(__file__))}/trans_times_str_cps.json", "w") as f:
    json.dump(all_transitions_times, f, indent=4)


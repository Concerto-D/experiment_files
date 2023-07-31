import json
import os

nb_scaling_sites = 15

all_transitions_times = {"transitions_times": {}}
transitions_times = all_transitions_times["transitions_times"]
transitions_times["mariadbmaster"] = {
    "configure0": 3.30,
    "configure1": 4.77,
    "bootstrap": 25.92,
    "start": 12.68,
    "register": 2.72,
    "deploy": 12.25,
    "interrupt": 0.48,
    "unconfigure": 3.28,
}
for i in range(nb_scaling_sites):
    transitions_times[f"mariadbworker{i}"] = {
        "configure0": 3.30,
        "configure1": 4.77,
        "bootstrap": 25.92,
        "start": 12.68,
        "register": 2.72,
        "deploy": 12.25,
        "interrupt": 0.48,
        "unconfigure": 3.28,
    }
    transitions_times[f"keystone{i}"] = {
        "pull": 3.30,
        "deploy": 77.59, # 77
        "turnoff": 3.76,
    }
    transitions_times[f"glance{i}"] = {
        "pull0": 5.0,
        "pull1": 7.14,
        "pull2": 15.7,
        "deploy": 62.72,  # 62
        "turnoff": 3.76,
    }
    transitions_times[f"nova{i}"] = {
        "pull0": 11.73,
        "pull1": 15.05,
        "pull2": 9.47,
        "ready0": 33.97,
        "ready1": 79.37,
        "start": 13.42,
        "deploy": 124.82,
        "cell_setup": 37.68,  # 124.82
        "interrupt": 0.48,
        "unpull": 3.28,
    }
    transitions_times[f"neutron{i}"] = {
        "pull0": 8.37,
        "pull1": 20.58,
        "pull2": 19.37,
        "deploy": 141.10,  # 141
        "turnoff": 3.76,
    }

with open(f"{os.path.dirname(os.path.realpath(__file__))}/trans_times_openstack.json", "w") as f:
    json.dump(all_transitions_times, f, indent=4)


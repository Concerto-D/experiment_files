import json
import os

nb_scaling_sites = 10

all_transitions_times = {"transitions_times": {}}
transitions_times = all_transitions_times["transitions_times"]
transitions_times["mariadbmaster"] = {
    "configure0": 1,
    "configure1": 1,
    "bootstrap": 1,
    "start": 1,
    "register": 1,
    "deploy": 1,
    "interrupt": 1,
    "unconfigure": 1,
}
for i in range(nb_scaling_sites):
    transitions_times[f"mariadbworker{i}"] = {
        "configure0": 1,
        "configure1": 1,
        "bootstrap": 1,
        "start": 1,
        "register": 1,
        "deploy": 1,
        "interrupt": 1,
        "unconfigure": 1,
    }
    transitions_times[f"keystone{i}"] = {
        "pull": 1.30,
        "deploy": 1.59, # 77
        "turnoff": 1,
    }
    transitions_times[f"glance{i}"] = {
        "pull0": 1.0,
        "pull1": 1.14,
        "pull2": 1.7,
        "deploy": 1.72,  # 62
        "turnoff": 1,
    }
    transitions_times[f"nova{i}"] = {
        "pull0": 1.73,
        "pull1": 1.05,
        "pull2": 1.47,
        "ready0": 1.97,
        "ready1": 1.37,
        "start": 1.68,
        "deploy": 1.42,
        "cell_setup": 1.82,  # 124.82
        "interrupt": 1,
        "unpull": 1,
    }
    transitions_times[f"neutron{i}"] = {
        "pull0": 1.37,
        "pull1": 1,
        "pull2": 1,
        "deploy": 1,  # 141
        "turnoff": 1,
    }

with open(f"{os.path.dirname(os.path.realpath(__file__))}/trans_times_openstack_trans_1.json", "w") as f:
    json.dump(all_transitions_times, f, indent=4)


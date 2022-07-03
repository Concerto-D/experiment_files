import json
import os
import random
import time
from datetime import datetime

import numpy as np


def compute_uptimes(freq, duration, nb_deps, overlap_taux, overlap_time_max, limit_nb_up_allowed):
    init_up_list = -1 if limit_nb_up_allowed else nb_deps
    up_list = [{"nb_up_allowed": init_up_list} for _ in range(freq)]
    nb_ups = [15, 15, 10, 15, 5]
    while any(up["nb_up_allowed"] == -1 for up in up_list):
        k = random.randint(0, freq - 1)
        d = random.randint(0, 4)
        if nb_ups[d] > 0 and up_list[k]["nb_up_allowed"] == -1:
            up_list[k]["nb_up_allowed"] = d
            nb_ups[d] -= 1

    min_taux, max_taux = overlap_taux
    amount_time_min = freq * duration * min_taux
    amount_time_max = freq * duration * max_taux

    nb_appearance_ok = False
    while not nb_appearance_ok:
        for dep_num in range(nb_deps):
            mu, sigma = 3, 1.1  # mean and standard deviation
            number_generator = np.random.lognormal(mu, sigma, 10000)
            number_generator = list(filter(lambda x: 1 < x <= overlap_time_max, number_generator))
            number_generator = iter(number_generator)
            amount_to_spread = random.uniform(amount_time_min, amount_time_max)
            s = time.time() + 2
            while amount_to_spread > 0.000001 and time.time() - s < 0:
                k = random.randint(0, freq - 1)
                current_up = up_list[k]
                nb_ups_assigned = len(current_up.keys()) - 1
                if dep_num not in current_up.keys() and current_up["nb_up_allowed"] > nb_ups_assigned:
                    min_o = next(number_generator) if limit_nb_up_allowed else random.uniform(0, overlap_time_max)
                    overlap = min(min_o, amount_to_spread)
                    current_up[dep_num] = overlap
                    amount_to_spread -= overlap

        # Print dep by appearance
        for dep_num in range(nb_deps):
            nb_appearance = 0
            for up in up_list:
                if dep_num in up.keys():
                    nb_appearance += 1
            print(f"dep{dep_num} appears {nb_appearance}")

        # Check nb appearances ok (>= 6)
        nb_appearance_ok = True
        for dep_num in range(nb_deps):
            nb_appearance = 0
            for up in up_list:
                if dep_num in up.keys():
                    nb_appearance += 1
            if nb_appearance < 6:
                nb_appearance_ok = False

        # Reset if its not ok
        if not nb_appearance_ok:
            for up in up_list:
                for dep_num in [key for key in up.keys() if key != "nb_up_allowed"]:
                    del up[dep_num]
            print("nb_appearance not ok")

    return up_list


def generate_uptimes_files(freq, duration, nb_deps, overlap_taux, nb_generations, overlap_time_max, limit_nb_up_allowed, perc_str):
    for i in range(nb_generations):
        up_list = compute_uptimes(freq, duration, nb_deps, overlap_taux, overlap_time_max, limit_nb_up_allowed=limit_nb_up_allowed)
        timestamp_log_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"generated_uptimes_for_{perc_str}_specific-{timestamp_log_dir}", "w") as f:
            print(f"dumping generated_uptimes_for_{perc_str}_specific-{timestamp_log_dir}")
            json.dump(up_list, f)
            time.sleep(1)


def see_uptimes_files(f):
    n = 0
    # for f in os.listdir():
    # if "generated_uptimes_for" in f:
    print(f"----- file {f} -------")
    with open(f) as lf:
        output = json.load(lf)

    # Print dep by appearance
    for dep_num in range(12):
        nb_appearance = 0
        for up in output:
            if str(dep_num) in up.keys():
                nb_appearance += 1
        print(f"dep{dep_num} appears {nb_appearance}")

    for up_num in range(len(output)):
        print(f"freq{up_num}: {output[up_num]}")

    print("---------------------")
    n += 1


def create_uptimes_nodes(uptimes_by_freq, freq, duration, nb_deps, overlap_taux, nb_generations):
    uptimes_nodes = [[] for _ in range(nb_deps + 1)]
    for up_num in range(freq):
        before_u = 130 * up_num
        uptime = before_u + duration + 5
        after_u = uptime + duration + 5
        uptimes_nodes[0].append((uptime, duration))
        for dep_num in range(nb_deps):
            current_up = uptimes_by_freq[up_num]
            pos = random.randint(1, 2)
            if str(dep_num) not in current_up.keys():
                if pos == 1:
                    uptimes_nodes[dep_num+1].append((before_u, duration))
                else:
                    uptimes_nodes[dep_num+1].append((after_u, duration))
            else:
                if pos == 1:
                    uptime_dep = uptime - (duration - current_up[str(dep_num)])
                else:
                    uptime_dep = uptime + (duration - current_up[str(dep_num)])
                uptimes_nodes[dep_num+1].append((uptime_dep, duration))

    for dep_num, u in enumerate(uptimes_nodes):
        print(f"dep_num {dep_num}", u[:7])

    return uptimes_nodes


def generate_uptimes_nodes_file(
    file_name, freq, duration, nb_deps, overlap_taux, nb_generations, perc_str
):
    with open(file_name) as f:
        uptimes_by_freq = json.load(f)
    uptimes_nodes = create_uptimes_nodes(uptimes_by_freq, freq, duration, nb_deps, overlap_taux, nb_generations)

    with open(f"uptimes/uptimes-60-30-12-{perc_str}-1.json", "w") as f:
        json.dump(uptimes_nodes, f)


if __name__ == "__main__":
    freq = 60
    duration = 30
    nb_deps = 12
    overlap_taux = (0.2, 0.3)
    nb_generations = 1
    # generate_uptimes_files(freq, duration, nb_deps, overlap_taux, nb_generations, 30, False, "0_2-0_3")
    # see_uptimes_files(file_name)
    file_name = "generated_uptimes_for_0_2-0_3_specific-2022-07-02_12-22-01"
    generate_uptimes_nodes_file(file_name, freq, duration, nb_deps, overlap_taux, nb_generations, "0_2-0_3")

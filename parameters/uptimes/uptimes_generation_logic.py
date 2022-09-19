import json
import os
import random
import sys
import time
from datetime import datetime

import numpy as np


def compute_uptimes(round, duration, nb_deps, overlap_taux, overlap_time_max, max_nb_up_allowed):
    init_up_list = -1 if max_nb_up_allowed else nb_deps
    up_list = [{"max_nb_up_allowed": init_up_list} for _ in range(round)]
    nb_ups = [15, 15, 10, 15, 5]
    while any(up["max_nb_up_allowed"] == -1 for up in up_list):
        k = random.randint(0, round - 1)
        d = random.randint(0, 4)
        if nb_ups[d] > 0 and up_list[k]["max_nb_up_allowed"] == -1:
            up_list[k]["max_nb_up_allowed"] = d
            nb_ups[d] -= 1

    min_taux, max_taux = overlap_taux
    amount_time_min = round * duration * min_taux
    amount_time_max = round * duration * max_taux
    perc_100_overlap = min_taux == max_taux == 1
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
                k = random.randint(0, round - 1)
                current_up = up_list[k]
                nb_ups_assigned = len(current_up.keys()) - 1
                if dep_num not in current_up.keys() and current_up["max_nb_up_allowed"] > nb_ups_assigned:
                    # to refacto le 100 perc overlap
                    if not perc_100_overlap:
                        min_o = next(number_generator) if max_nb_up_allowed else random.uniform(0, overlap_time_max)
                    else:
                        min_o = duration
                    overlap = min(min_o, amount_to_spread)
                    current_up[dep_num] = overlap
                    amount_to_spread -= overlap

        # Print dep by appearance
        for dep_num in range(nb_deps):
            nb_appearance = 0
            for up in up_list:
                if dep_num in up.keys():
                    nb_appearance += 1
            print(f"dep{dep_num} appears {nb_appearance} times")

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
                for dep_num in [key for key in up.keys() if key != "max_nb_up_allowed"]:
                    del up[dep_num]
            print("nb_appearance not ok")

    return up_list


def generate_uptimes_per_dep_num_files(round, duration, nb_deps, overlap_taux, nb_generations, overlap_time_max, max_nb_up_allowed, perc_str):
    for i in range(nb_generations):
        up_list = compute_uptimes(round, duration, nb_deps, overlap_taux, overlap_time_max, max_nb_up_allowed=max_nb_up_allowed)
        timestamp_log_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(f"uptimes_per_dep_num_for_{perc_str}_overlap-{timestamp_log_dir}", "w") as f:
            print(f"Generated file: generated_uptimes_for_{perc_str}_specific-{timestamp_log_dir}")
            json.dump(up_list, f)
            time.sleep(1)


def see_uptimes_files(f):
    n = 0
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
        print(f"round{up_num}: {output[up_num]}")

    print("---------------------")
    n += 1


def create_uptimes_nodes(uptimes_by_round, round, duration, nb_deps, overlap_taux, nb_generations, perc_100_overlap):
    uptimes_nodes = [[] for _ in range(nb_deps + 1)]
    for up_num in range(round):
        offset = 130 if not perc_100_overlap else 65
        before_u = offset * up_num
        uptime = before_u + (duration if not perc_100_overlap else 0)
        after_u = uptime + duration + 5
        uptimes_nodes[0].append((uptime, duration))
        for dep_num in range(nb_deps):
            if perc_100_overlap:
                uptimes_nodes[dep_num+1].append((uptime, duration))
            else:
                current_up = uptimes_by_round[up_num]
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
    file_name, round, duration, nb_deps, overlap_taux, nb_generations, perc_str, perc_100_overlap
):
    with open(file_name) as f:
        uptimes_by_round = json.load(f)
    uptimes_nodes = create_uptimes_nodes(uptimes_by_round, round, duration, nb_deps, overlap_taux, nb_generations, perc_100_overlap)

    with open(f"uptimes/uptimes-60-30-12-{perc_str}-zefezf.json", "w") as f:
        json.dump(uptimes_nodes, f)


if __name__ == "__main__":
    round = 60
    duration = 30
    nb_deps = 12
    overlap_taux = (0.2, 0.3)
    nb_generations = 1

    print("Select order: generate, see <file_name>, compute <file_name>")
    order = sys.argv[1] if len(sys.argv) > 1 else ""
    if order == "generate":
        generate_uptimes_per_dep_num_files(round, duration, nb_deps, overlap_taux, nb_generations, 30, False, "1-1")
    elif order == "see":
        file_name = sys.argv[2]
        see_uptimes_files(file_name)
    elif order == "compute":
        file_name = sys.argv[2]
        perc_100_overlap = overlap_taux == (1, 1)
        generate_uptimes_nodes_file(file_name, round, duration, nb_deps, overlap_taux, nb_generations, "1-1", perc_100_overlap)
    else:
        print("Wrong order")


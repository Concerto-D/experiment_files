import copy
import json
import os
import random
import sys
import time
from datetime import datetime

import numpy as np


def compute_uptimes(round, duration, nb_deps, overlap_taux, overlap_time_max, max_nb_up_allowed, nb_zero_overlap_rounds=0):
    """
    Brute force way to compute overlaps until the percentage and conditions are met
    """
    init_up_list = nb_deps
    up_list = [{"max_nb_up_allowed": init_up_list} for _ in range(round)]
    # for zero_round in random.sample(range(len(up_list)), nb_zero_overlap_rounds):
    #     up_list[zero_round]["max_nb_up_allowed"] = 0

    if max_nb_up_allowed:
        # nb_ups = [15, 15, 10, 15, 5]
        nb_ups = [3, 5, 13, 10, 5]  # Tweak these values
        while any(nb_up > 0 for nb_up in nb_ups):
            k = random.randint(0, round - 1)
            d = random.randint(0, 4)
            if nb_ups[d] > 0 and up_list[k]["max_nb_up_allowed"] == nb_deps:
                up_list[k]["max_nb_up_allowed"] = d
                nb_ups[d] -= 1

    min_taux, max_taux = overlap_taux
    amount_time_min = round * duration * min_taux
    amount_time_max = round * duration * max_taux
    perc_100_overlap = min_taux == max_taux == 1
    nb_appearance_ok = False
    while not nb_appearance_ok:
        for dep_num in range(nb_deps):
            amount_to_spread_to_search = random.uniform(amount_time_min, amount_time_max)
            save_uplist = copy.deepcopy(up_list)
            amount_to_spread = amount_to_spread_to_search
            # while amount_to_spread > 0.001 and time.time() - s < 0:
            while amount_to_spread > 0.001:
                # Check if need to reset
                no_room = True
                for up in up_list:
                    if dep_num not in up.keys() and up["max_nb_up_allowed"] > len(up.keys()) - 1:
                        no_room = False
                if amount_to_spread > 0.001 and no_room:
                    print(amount_to_spread)
                    up_list = copy.deepcopy(save_uplist)
                    amount_to_spread = amount_to_spread_to_search

                k = random.randint(0, round - 1)
                current_up = up_list[k]
                nb_ups_assigned = len(current_up.keys()) - 1
                if dep_num not in current_up.keys() and current_up["max_nb_up_allowed"] > nb_ups_assigned:
                    # to refacto le 100 perc overlap
                    if not perc_100_overlap:
                        min_o = random.uniform(6, duration)  # Tweak these values
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


def generate_uptimes_per_dep_num_files(round, duration, nb_deps, overlap_taux, nb_generations, overlap_time_max, max_nb_up_allowed, perc_str, nb_zero_overlap_rounds=0):
    up_list = compute_uptimes(round, duration, nb_deps, overlap_taux, overlap_time_max, max_nb_up_allowed=max_nb_up_allowed, nb_zero_overlap_rounds=nb_zero_overlap_rounds)
    timestamp_log_dir = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    uptimes_file_name = f"uptimes_per_dep_num_for_{perc_str}_overlap-{timestamp_log_dir}"
    with open(uptimes_file_name, "w") as f:
        print(f"Generated file: {uptimes_file_name}")
        json.dump(up_list, f)
        time.sleep(1)

    return uptimes_file_name


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

        offset = duration * 4 + 10 if not perc_100_overlap else duration * 2 + 5
        before_u = offset * up_num
        uptime = before_u + (duration if not perc_100_overlap else 0) + 5
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

    with open(f"uptimes-{round}-{duration}-{nb_deps}-{perc_str}-re-generated.json", "w") as f:
        json.dump(uptimes_nodes, f)


if __name__ == "__main__":
    round = 36
    duration = 50
    nb_deps = 12
    overlap_taux = (0.02, 0.02)
    nb_generations = 1  # Keep it a 1 bc it will always generate 1 TODO: remove this param
    overlap_taux_str = f"{str(overlap_taux[0]).replace('.', '_')}-{str(overlap_taux[1]).replace('.', '_')}"

    order = sys.argv[1] if len(sys.argv) > 1 else "generate"
    if order == "generate":
        uptimes_file_name = generate_uptimes_per_dep_num_files(round, duration, nb_deps, overlap_taux, nb_generations, duration, False, overlap_taux_str, nb_zero_overlap_rounds=5)
        perc_100_overlap = overlap_taux == (1, 1)
        generate_uptimes_nodes_file(uptimes_file_name, round, duration, nb_deps, overlap_taux, nb_generations, overlap_taux_str, perc_100_overlap)
    elif order == "see":
        file_name = sys.argv[2]
        see_uptimes_files(file_name)
    else:
        print("Args: generate, see <file_name> or compute <file_name>")

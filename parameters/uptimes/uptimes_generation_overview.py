import json
import os
import random
import time
from datetime import datetime
from itertools import product
from os.path import exists
from typing import List, Dict, Tuple
import matplotlib
import yaml
from matplotlib import pyplot as plt
import numpy as np


dir_name = "../generations"


def generate_uptimes_by_params(
        rounds_awake_list: List[int],
        time_awakening: List[int],
        nb_deps_list: List[int],
        overlap_percentages_list: List[Tuple],
        max_bound: int,
        step_range: int,
        offset_between_draw: int
) -> Dict:
    """
    TODO: reprendre le nom des variables (time, nb_deps, etc)
    returns: Dict de la forme:
    {(nb_de_reveils, temps_awoken, nb_OU_deps): {taux_1: [temps_reveils_list_ou1, temps_reveils_list_ou2, ...], ...}, ...}
    """
    uptimes_by_params = {}
    # Compute each possible combination between parameters
    for round, duration, nb_deps in product(rounds_awake_list, time_awakening, nb_deps_list):
        covering_perc_values = {}
        for overlap_tuple in overlap_percentages_list:
            covering_perc_values[overlap_tuple] = None

        # We want to have uptimes for each choosen percentage value
        # TODO: voir si ça prend trop de temps on met une condition d'arrêt
        while not all(uptimes is not None for uptimes in covering_perc_values.values()):
            # On écarte de plus en plus la plage sur laquelle choisir les uptimes
            gap = 100
            uptimes_list = compute_uptimes_for_params(round, nb_deps, 100, duration, 10, offset_between_draw)

            # Check if uptimes overlap fits into category
            dep_num = 0    # Check only server
            cov_perc_list = compute_covering_time_dep(dep_num, round, duration, uptimes_list)
            server_means_coverage = round(sum(cov_perc_list)/len(cov_perc_list), 2)
            print(f"Server coverage: {server_means_coverage}% for gap {gap}")
            for cover_val in covering_perc_values.keys():
                # TODO Mettre des intervals plus larges, entre 0.1 et 0.2, au lieu d'une valeur fixe
                if covering_perc_values[cover_val] is None and cover_val[0] <= server_means_coverage <= cover_val[1]:
                    print(f"Found for {(round, duration, nb_deps)} {cover_val}")
                    covering_perc_values[cover_val] = uptimes_list

        uptimes_by_params[(round, duration, nb_deps)] = covering_perc_values

    return uptimes_by_params


def compute_uptimes_for_params(round, nb_deps, gap, duration, spread, offset_between_draw):
    uptimes_list = [[] for _ in range(nb_deps + 1)]
    for up_num in range(round):
        b_min = gap * up_num + offset_between_draw * up_num
        b_max = gap * (up_num+1) + (duration*up_num - duration)
        mu, sigma = (b_min + b_max)/2, spread  # mean and standard deviation
        number_generator = list(filter(lambda x: b_min <= x <= b_max, np.random.normal(mu, sigma, 500)))
        number_generator = iter(number_generator)
        for dep_num in range(nb_deps + 1):  # Add 1 to the nb_deps to add the server
            uptimes_list[dep_num].append((next(number_generator), duration))
    return tuple(tuple(uptimes) for uptimes in uptimes_list)


def compute_covering_time_dep(dep_num: int, round: int, time_awoken: float, all_dep_uptimes):
    uptimes_dep = all_dep_uptimes[dep_num]
    all_other_uptimes = [all_dep_uptimes[i] for i in range(len(all_dep_uptimes)) if dep_num != i]
    overlaps_list = []
    for other_uptimes_dep in all_other_uptimes:
        covering_time = 0
        for uptime_dep in uptimes_dep:
            for other_uptime_dep in other_uptimes_dep:
                overlap = min(uptime_dep[0] + time_awoken, other_uptime_dep[0] + time_awoken) - max(uptime_dep[0], other_uptime_dep[0])
                covering_time += overlap if overlap > 0 else 0

        percentage_overlap = covering_time/(time_awoken*round)
        overlaps_list.append(percentage_overlap)

    return overlaps_list


def plot_uptimes(uptimes_by_params, datetime_now_formatted: str):
    # Configure to plot on images instead of screen
    matplotlib.use('Agg')

    line_number = 5      # Line number to plot uptimes, one line per OU
    figure_number = 0    # Figure number to plot

    # For each combination of param, plot figure by covering percentage
    for params, uptimes_to_plot in uptimes_by_params.items():
        # Create dir to storage images for specific param combination
        round, duration, nb_deps = params

        # Create image for each covering percentage
        for perc, all_uptimes in uptimes_to_plot.items():
            plt.figure(figure_number)
            if all_uptimes is None: continue
            for uptimes_ou in all_uptimes:
                color_number = 0
                for uptime_tuple in uptimes_ou:
                    uptime, duration = uptime_tuple
                    start = uptime
                    end = uptime + duration
                    plt.plot([start, end], [line_number, line_number], 'br'[color_number])
                    color_number = not color_number
                line_number -= 0.5  # Decrease to print next OU
            plt.plot([1, 3], [8, 8], 'w')   # Used to get lines closer together (else it is spread vertically)
            min_p, max_p = perc
            min_p = str(min_p).replace(".", "_")
            max_p = str(max_p).replace(".", "_")
            plt.savefig(f"{dir_name}/{datetime_now_formatted}/figure-{round}-{duration}-{nb_deps}-{min_p}-{max_p}.png")
            plt.close(figure_number)
            figure_number += 1
            line_number = 5


def main():
    # Compute uptimes
    rounds_awake_list = [60]
    time_awakening = [30]
    nb_deps_list = [12]
    overlap_percentages_list = [(0.5, 0.6)]
    max_bound = 4000
    step_range = 1
    offset_between_draw = 30
    uptimes_by_params = generate_uptimes_by_params(
        rounds_awake_list,
        time_awakening,
        nb_deps_list,
        overlap_percentages_list,
        max_bound,
        step_range,
        offset_between_draw
    )
    print("finished")

    datetime_now_formatted = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    os.makedirs(f"{dir_name}/{datetime_now_formatted}", exist_ok=True)
    for params, overlap_values in uptimes_by_params.items():
        round, duration, nb_deps = params
        for overlap_perc, uptimes in overlap_values.items():
            min_p, max_p = overlap_perc
            min_p = str(min_p).replace(".", "_")
            max_p = str(max_p).replace(".", "_")
            file_name = f"{dir_name}/{datetime_now_formatted}/uptimes-{round}-{duration}-{nb_deps}-{min_p}-{max_p}.json"
            with open(file_name, "w") as f:
                json.dump(uptimes, f)

    # Plot uptimes
    plot_uptimes(uptimes_by_params, datetime_now_formatted)


if __name__ == '__main__':
    main()

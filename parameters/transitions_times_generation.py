import json
import random
from typing import Tuple


def generate_server_transitions_time(nb_deps: int, min_value: float = 10., max_value: float = 60.) -> Tuple:
    server_t_sa = round(random.uniform(min_value, max_value), 2)
    server_t_sc = tuple(round(random.uniform(min_value, max_value), 2) for i in range(nb_deps))
    server_t_sr = round(random.uniform(min_value, max_value), 2)
    server_t_ss = tuple(round(random.uniform(min_value, max_value), 2) for i in range(nb_deps))
    server_t_sp = tuple(round(random.uniform(min_value, max_value), 2) for i in range(nb_deps))
    return tuple({
        "t_sa": server_t_sa,
        "t_sc": server_t_sc,
        "t_sr": server_t_sr,
        "t_ss": server_t_ss,
        "t_sp": server_t_sp,
    }.items())


def generate_deps_transitions_time(dep_num: int, min_value: float = 10., max_value: float = 60.) -> Tuple:
    deps_t_di = round(random.uniform(min_value, max_value), 2)
    deps_t_dr = round(random.uniform(min_value, max_value), 2)
    deps_t_du = round(random.uniform(min_value, max_value), 2)
    return tuple({
        "id": dep_num,
        "t_di": deps_t_di,
        "t_dr": deps_t_dr,
        "t_du": deps_t_du,
    }.items())


def generate_transitions_times(nb_deps_exp: int, nb_generations: int, min_value: int, max_value: int):
    all_generations_transitions_times = []
    for _ in range(nb_generations):
        generations_tt = [generate_server_transitions_time(nb_deps_exp, min_value, max_value)]
        for dep_num in range(nb_deps_exp):
            generations_tt.append(generate_deps_transitions_time(dep_num, min_value, max_value))
        all_generations_transitions_times.append(tuple(generations_tt))
    return all_generations_transitions_times


def generate_transitions_time_file(transitions_times, nb_nodes):
    print("------ Creating configuration file for reconfiguration programs --------")
    transitions_to_dump = {"server": dict(transitions_times[0])}
    for dep_num in range(1, nb_nodes):
        transitions_to_dump[f"dep{dep_num - 1}"] = dict(transitions_times[dep_num])
    hash_file = str(abs(hash(transitions_times)))[:6]
    reconf_config_file = f"generations/transitions_times_{hash_file}.json"
    with open(reconf_config_file, "w") as f:
        json.dump({"nb_deps_tot": nb_nodes - 1, "transitions_time": transitions_to_dump}, f, indent=4)
    print(f"Config file saved in {reconf_config_file}")
    return hash_file, reconf_config_file


if __name__ == "__main__":
    nb_deps = 20
    nb_generations = 2
    min_value = 1
    max_value = 30
    transitions_times_list = generate_transitions_times(nb_deps, nb_generations, min_value, max_value)
    for trans_time in transitions_times_list:
        generate_transitions_time_file(trans_time, nb_deps + 1)

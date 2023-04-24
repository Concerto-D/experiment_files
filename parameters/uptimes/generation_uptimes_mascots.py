# Choisir 45 uniques valeurs entre 0 et 59 uniformément distribuées pour chaque noeud
# Créer les deps dans le spot 0 ou 2 (choisir 0 ou 2 de manière random):
# slot_duration = uptime_duration + offset
# total_interval_duration = slot_duration*3 + maxttoffset
#   - 0: [i*total_interval_duration, (i+1)*total_interval_duration + slot_duration]
#   - 1: [i*total_interval_duration + slot_duration, (i+1)*total_interval_duration + slot_duration*2]
#   - 2: [i*total_interval_duration + slot_duration*2, (i+1)*total_interval_duration + slot_duration*3 + maxttoffset]
from typing import List

# Choisir 20 uniques valeurs entre 0 et 59 uniformément distribuées pour chaque noeud sauf le serveur
# Créer un overlap de 1 sec pour chaque round correspond aux valeurs choisies (ajuster le point de départ en ajoutant 6 sec ou diminuant de 6 sec)

# Répartir les temps via une distribution uniforme pour choisir les overlaps à rallonger, lognormal pour choisir le temps à rajouter
import numpy as np


def generate_uptimes(
        nb_rounds: int = 40,
        total_ups_per_node: int = 30,
        uptime_duration: int = 50,
        offset: int = 5,
        max_transition_time_offset: int = 30,
        nb_nodes: int = 13
):
    # TODO: remplacer par la nouvelle façon de faire np.Generate (seedée)
    # Generate all rounds per node with uptime
    all_uptime_rounds_up = []
    for node_num in range(nb_nodes):
        uptime_schedule = sorted(np.random.choice(nb_rounds, total_ups_per_node, replace=False))
        all_uptime_rounds_up.append(uptime_schedule)

    # Setup variable for the uptime calculation formula
    slot_duration = uptime_duration + offset
    total_interval_duration = slot_duration * 3 + max_transition_time_offset

    # Create the schedule for the nodes:
    # - server occupy slot 1
    # - deps occupy either slot 0 or 2
    nodes_schedules_list = []
    for node_num in range(nb_nodes):
        node_schedule = []
        for uptime_round in range(nb_rounds):
            if uptime_round in all_uptime_rounds_up[node_num]:
                slot_num = np.random.choice([0, 2]) if node_num > 0 else 1  # Slot num for server == 1
                node_schedule.append((uptime_round*total_interval_duration + slot_duration*slot_num, slot_num))
            else:
                node_schedule.append(-1)
        nodes_schedules_list.append(node_schedule)

    return nodes_schedules_list


def generate_overlaps(nodes_schedules_list: List[List[int]], nb_rounds: int = 40, total_nb_overlaps_deps: int = 15):
    # Generate rounds with overlap for each dep
    all_deps_overlap_rounds = []
    for node_num in range(len(nodes_schedules_list[1:])):
        dep_overlap_rounds = np.random.choice(nb_rounds, total_nb_overlaps_deps, replace=False)
        all_deps_overlap_rounds.append(dep_overlap_rounds)

    # Create overlaps dep/server for each round with overlap
    for dep_num in range(1, len(all_deps_overlap_rounds) + 1):
        for round_overlap in all_deps_overlap_rounds[dep_num]:
            print(dep_num, round_overlap)
            # TODO: Gérer pour les overlaps les moments où il ne se réveille pas
            initial_uptime, slot_num = nodes_schedules_list[dep_num][round_overlap]
            updated_uptime = initial_uptime + (6 if slot_num == 0 else -6)
            nodes_schedules_list[dep_num][round_overlap] = (updated_uptime, slot_num)

    print(nodes_schedules_list)


nodes_schedules_list = generate_uptimes()
generate_overlaps(nodes_schedules_list)


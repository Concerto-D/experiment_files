# Choisir 45 uniques valeurs entre 0 et 59 uniformément distribuées pour chaque noeud
# Créer les deps dans le spot 0 ou 2 (choisir 0 ou 2 de manière random):
# slot_duration = uptime_duration + offset
# total_interval_duration = slot_duration*3 + maxttoffset
#   - 0: [i*total_interval_duration, (i+1)*total_interval_duration + slot_duration]
#   - 1: [i*total_interval_duration + slot_duration, (i+1)*total_interval_duration + slot_duration*2]
#   - 2: [i*total_interval_duration + slot_duration*2, (i+1)*total_interval_duration + slot_duration*3 + maxttoffset]
from typing import List, Tuple

# Choisir 20 uniques valeurs entre 0 et 59 uniformément distribuées pour chaque noeud sauf le serveur
# Créer un overlap de 1 sec pour chaque round correspond aux valeurs choisies (ajuster le point de départ en ajoutant 6 sec ou diminuant de 6 sec)

# Répartir les temps via une distribution uniforme pour choisir les overlaps à rallonger, lognormal pour choisir le temps à rajouter
import numpy as np

RANDOM_GENERATION_SEED = 948371
NON_UP_ROUND = -1

random_generator = np.random.default_rng(RANDOM_GENERATION_SEED)


def generate_uptimes(
        nb_rounds: int = 40,
        total_ups_per_node: int = 30,
        uptime_duration: int = 50,
        offset: int = 5,
        max_transition_time_offset: int = 30,
        nb_nodes: int = 13
):
    # Generate all rounds per node with uptime
    all_uptime_rounds_up = []
    for node_num in range(nb_nodes):
        uptime_schedule = sorted(random_generator.choice(nb_rounds, total_ups_per_node, replace=False))
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
                slot_num = random_generator.choice([0, 2]) if node_num > 0 else 1  # Slot num for server == 1
                node_schedule.append((uptime_round*total_interval_duration + slot_duration*slot_num, slot_num))
            else:
                node_schedule.append(NON_UP_ROUND)
        nodes_schedules_list.append(node_schedule)

    return nodes_schedules_list


def generate_overlaps(nodes_schedules_list: List[List[Tuple[int, int]]], nb_rounds: int = 40, total_nb_overlaps_deps: int = 15):
    # Extract server rounds where it is up
    server_rounds_up = [i for i, round_server in enumerate(nodes_schedules_list[0]) if round_server != NON_UP_ROUND]

    # Generate rounds with overlap for each dep
    all_deps_overlap_rounds = []
    deps_schedules_list = nodes_schedules_list[1:]
    for dep_num in range(len(deps_schedules_list)):
        # Get matching up-time rounds
        matching_rounds_server_dep = [r for r in server_rounds_up if r in [i for i, round_dep in enumerate(deps_schedules_list[dep_num]) if round_dep != NON_UP_ROUND]]
        dep_overlap_rounds = random_generator.choice(matching_rounds_server_dep, total_nb_overlaps_deps, replace=False)
        all_deps_overlap_rounds.append(dep_overlap_rounds)

    # Create overlaps dep/server for each round with overlap
    for dep_num in range(len(all_deps_overlap_rounds)):
        for round_overlap in all_deps_overlap_rounds[dep_num]:
            # Should never get a NON_UP_ROUND
            initial_uptime, slot_num = deps_schedules_list[dep_num][round_overlap]
            updated_uptime = initial_uptime + (6 if slot_num == 0 else -6)
            deps_schedules_list[dep_num][round_overlap] = (updated_uptime, slot_num)

    print(nodes_schedules_list)


nodes_schedules_list = generate_uptimes()
generate_overlaps(nodes_schedules_list)


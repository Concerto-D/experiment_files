# Choisir 45 uniques valeurs entre 0 et 59 uniformément distribuées pour chaque noeud
# Créer les deps dans le spot 0 ou 2 (choisir 0 ou 2 de manière random):
# slot_duration = uptime_duration + offset
# total_interval_duration = slot_duration*3 + maxttoffset
#   - 0: [i*total_interval_duration, (i+1)*total_interval_duration + slot_duration]
#   - 1: [i*total_interval_duration + slot_duration, (i+1)*total_interval_duration + slot_duration*2]
#   - 2: [i*total_interval_duration + slot_duration*2, (i+1)*total_interval_duration + slot_duration*3 + maxttoffset]
import copy
import json
from typing import List, Tuple, Set

# Choisir 20 uniques valeurs entre 0 et 59 uniformément distribuées pour chaque noeud sauf le serveur
# Créer un overlap de 1 sec pour chaque round correspond aux valeurs choisies (ajuster le point de départ en ajoutant 6 sec ou diminuant de 6 sec)

# Répartir les temps via une distribution uniforme pour choisir les overlaps à rallonger, lognormal pour choisir le temps à rajouter
import numpy as np

RANDOM_GENERATION_SEED = 948371
NON_UP_ROUND = (-1, -1)

random_generator = np.random.default_rng(RANDOM_GENERATION_SEED)
nb_rounds = 60
total_ups_per_node = 45
uptime_duration = 50
offset = 5
max_transition_time_offset = 30
nb_nodes = 6
total_nb_overlaps_deps = 30


def generate_uptimes_distribution(
        mandatory_rounds: List[Set] = None,
):
    if mandatory_rounds is None:
        mandatory_rounds = [[]]*nb_nodes

    # Generate all rounds per node with uptime
    all_uptime_rounds_up = []
    for node_num in range(nb_nodes):
        possible_rounds = set(range(nb_rounds)) - set([r[0] for r in mandatory_rounds[node_num]])
        uptime_schedule = sorted(random_generator.choice(list(possible_rounds), total_ups_per_node - len(mandatory_rounds[node_num]), replace=False))
        all_uptime_rounds_up.append(uptime_schedule)

    # Setup variable for the uptime calculation formula
    slot_duration = uptime_duration + offset
    total_interval_duration = slot_duration * 3 + max_transition_time_offset

    # Create the schedule for the nodes:
    # - server occupy slot 1
    # - deps occupy either slot 0 or 2
    uptimes_distribution_per_node = []
    for node_num in range(nb_nodes):
        node_schedule = []
        for uptime_round in range(nb_rounds):
            slot_num = random_generator.choice([0, 2]) if node_num > 0 else 1  # Slot num for server == 1
            if uptime_round in [r[0] for r in mandatory_rounds[node_num]]:
                for i, r in enumerate(mandatory_rounds[node_num]):
                    if r[0] == uptime_round:
                        s = 1 if node_num == 0 else r[1]  # Reprise du slot num: fix bug TODO à simplifier
                        node_schedule.append((uptime_round*total_interval_duration + slot_duration*s, s))
                        break
            elif uptime_round in all_uptime_rounds_up[node_num]:
                node_schedule.append((uptime_round*total_interval_duration + slot_duration*slot_num, slot_num))
            else:
                node_schedule.append(NON_UP_ROUND)
        uptimes_distribution_per_node.append(node_schedule)

    return uptimes_distribution_per_node


def _get_matching_rounds(server_rounds: List[Tuple[int, int]], dep_rounds: List[Tuple[int, int]]):
    # Extract server rounds where it is up
    server_rounds_up = [i for i, round_server in enumerate(server_rounds) if round_server != NON_UP_ROUND]
    matching_rounds_server_dep = [r for r in server_rounds_up if r in [i for i, round_dep in enumerate(dep_rounds) if round_dep != NON_UP_ROUND]]

    return matching_rounds_server_dep


def _generate_overlap_distribution_per_dep(uptimes_distribution_per_node: List[List[Tuple[int, int]]]):
    overlaps_distribution_per_dep = []
    deps_uptimes_distribution = uptimes_distribution_per_node[1:]
    for dep_num in range(len(deps_uptimes_distribution)):
        # Get matching up-time rounds
        matching_rounds_server_dep = _get_matching_rounds(uptimes_distribution_per_node[0], deps_uptimes_distribution[dep_num])
        dep_overlap_rounds = random_generator.choice(matching_rounds_server_dep, total_nb_overlaps_deps, replace=False)
        overlaps_distribution_per_dep.append(list(dep_overlap_rounds))

    return overlaps_distribution_per_dep


def generate_overlaps_distribution_from_uptimes(uptimes_distribution_per_node: List[List[Tuple[int, int]]]):
    # Generate rounds with overlap for each dep
    overlaps_distribution_per_dep = _generate_overlap_distribution_per_dep(uptimes_distribution_per_node)

    # Add the slot for each overlap round for each dep
    deps_uptimes_distribution = uptimes_distribution_per_node[1:]
    for dep_num in range(len(overlaps_distribution_per_dep)):
        for i in range(len(overlaps_distribution_per_dep[dep_num])):
            r = overlaps_distribution_per_dep[dep_num][i]
            overlaps_distribution_per_dep[dep_num][i] = (r, deps_uptimes_distribution[dep_num][r][1])

    # Diminish overlap distribution to 15 and 7 overlaps
    overlaps_distribution_per_dep_and_nb_overlaps = {
        "30": copy.deepcopy(overlaps_distribution_per_dep),
    }
    for dep_num in range(len(overlaps_distribution_per_dep)):
        indexes_to_remove = random_generator.choice(len(overlaps_distribution_per_dep[dep_num]), 15, replace=False)
        overlaps_to_remove = [overlaps_distribution_per_dep[dep_num][i] for i in indexes_to_remove]
        for overlap in overlaps_to_remove:
            overlaps_distribution_per_dep[dep_num].remove(overlap)
    overlaps_distribution_per_dep_and_nb_overlaps["15"] = copy.deepcopy(overlaps_distribution_per_dep)

    for dep_num in range(len(overlaps_distribution_per_dep)):
        indexes_to_remove = random_generator.choice(len(overlaps_distribution_per_dep[dep_num]), 8, replace=False)
        overlaps_to_remove = [overlaps_distribution_per_dep[dep_num][i] for i in indexes_to_remove]
        for overlap in overlaps_to_remove:
            overlaps_distribution_per_dep[dep_num].remove(overlap)
    overlaps_distribution_per_dep_and_nb_overlaps["7"] = copy.deepcopy(overlaps_distribution_per_dep)

    return overlaps_distribution_per_dep_and_nb_overlaps


def add_overlaps_to_uptimes_distribution(uptimes_distribution_per_node, overlaps_distribution_per_dep, duration_overlap):
    uptimes_distribution_per_node_copy = copy.deepcopy(uptimes_distribution_per_node)
    # Create overlaps dep/server for each round with overlap
    deps_uptimes_distribution = uptimes_distribution_per_node_copy[1:]
    for dep_num in range(len(overlaps_distribution_per_dep)):
        for round_overlap in overlaps_distribution_per_dep[dep_num]:
            round_overlap, slot_overlap = round_overlap
            # Should never get a NON_UP_ROUND
            initial_uptime, slot_num = deps_uptimes_distribution[dep_num][round_overlap]
            overlap_offset = offset + duration_overlap
            updated_uptime = initial_uptime + (overlap_offset if slot_num == 0 else -overlap_offset)
            deps_uptimes_distribution[dep_num][round_overlap] = (updated_uptime, slot_num)

    return uptimes_distribution_per_node_copy


def generate_uptimes_distribution_from_overlaps(overlaps_distribution_per_dep):
    server_mandatory_rounds = set()
    for rounds_overlap in overlaps_distribution_per_dep:
        for round_overlap in rounds_overlap:
            if round_overlap[0] not in [r[0] for r in server_mandatory_rounds]:
                server_mandatory_rounds.add(round_overlap)

    mandatory_rounds = [server_mandatory_rounds]

    for dep_num in range(len(overlaps_distribution_per_dep)):
        dep_mantory_rounds = set()
        for round_overlap in overlaps_distribution_per_dep[dep_num]:
            if round_overlap[0] not in [r[0] for r in dep_mantory_rounds]:
                dep_mantory_rounds.add(round_overlap)

        mandatory_rounds.append(dep_mantory_rounds)

    return generate_uptimes_distribution(mandatory_rounds=mandatory_rounds)


if __name__ == '__main__':
    # Create ud0, od0
    ud0 = generate_uptimes_distribution()
    od0 = generate_overlaps_distribution_from_uptimes(ud0)

    # Create ud1 and ud2
    ud1 = generate_uptimes_distribution_from_overlaps(od0["15"])
    ud2 = generate_uptimes_distribution_from_overlaps(od0["15"])

    # Create od1 and od2
    od1 = generate_overlaps_distribution_from_uptimes(ud0)
    od2 = generate_overlaps_distribution_from_uptimes(ud0)

    # Base
    ud0_od0_15_25_perc = add_overlaps_to_uptimes_distribution(ud0, od0["15"], duration_overlap=12.5)

    # ud
    ud1_od0_15_25_perc = add_overlaps_to_uptimes_distribution(ud1, od0["15"], duration_overlap=12.5)
    ud2_od0_15_25_perc = add_overlaps_to_uptimes_distribution(ud2, od0["15"], duration_overlap=12.5)

    # od
    ud0_od1_15_25_perc = add_overlaps_to_uptimes_distribution(ud0, od1["15"], duration_overlap=12.5)
    ud0_od2_15_25_perc = add_overlaps_to_uptimes_distribution(ud0, od2["15"], duration_overlap=12.5)

    # nb
    ud0_od0_7_25_perc = add_overlaps_to_uptimes_distribution(ud0, od0["7"], duration_overlap=12.5)
    ud0_od0_30_25_perc = add_overlaps_to_uptimes_distribution(ud0, od0["30"], duration_overlap=12.5)

    # perc
    ud0_od0_15_2_perc = add_overlaps_to_uptimes_distribution(ud0, od0["15"], duration_overlap=1)
    ud0_od0_15_50_perc = add_overlaps_to_uptimes_distribution(ud0, od0["15"], duration_overlap=25)

    def convert_int64_to_int(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        raise TypeError(f'Type {type(obj)} non sérialisable')

    # Base
    with open(f"mascots_uptimes-60-50-5-ud0_od0_15_25_perc.json", "w") as f:
        json.dump(ud0_od0_15_25_perc, f, default=convert_int64_to_int)

    # ud
    with open(f"mascots_uptimes-60-50-5-ud1_od0_15_25_perc.json", "w") as f:
        json.dump(ud1_od0_15_25_perc, f, default=convert_int64_to_int)
    with open(f"mascots_uptimes-60-50-5-ud2_od0_15_25_perc.json", "w") as f:
        json.dump(ud2_od0_15_25_perc, f, default=convert_int64_to_int)

    # od
    with open(f"mascots_uptimes-60-50-5-ud0_od1_15_25_perc.json", "w") as f:
        json.dump(ud0_od1_15_25_perc, f, default=convert_int64_to_int)
    with open(f"mascots_uptimes-60-50-5-ud0_od2_15_25_perc.json", "w") as f:
        json.dump(ud0_od2_15_25_perc, f, default=convert_int64_to_int)

    # nb
    with open(f"mascots_uptimes-60-50-5-ud0_od0_7_25_perc.json", "w") as f:
        json.dump(ud0_od0_7_25_perc, f, default=convert_int64_to_int)
    with open(f"mascots_uptimes-60-50-5-ud0_od0_30_25_perc.json", "w") as f:
        json.dump(ud0_od0_30_25_perc, f, default=convert_int64_to_int)

    # perc
    with open(f"mascots_uptimes-60-50-5-ud0_od0_15_2_perc.json", "w") as f:
        json.dump(ud0_od0_15_2_perc, f, default=convert_int64_to_int)
    with open(f"mascots_uptimes-60-50-5-ud0_od0_15_50_perc.json", "w") as f:
        json.dump(ud0_od0_15_50_perc, f, default=convert_int64_to_int)

    print()

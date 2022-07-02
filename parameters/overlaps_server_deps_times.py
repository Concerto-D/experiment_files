import json
import sys


def compute_covering_time_dep(dep_num: int, freq: int, time_awoken: float, all_dep_uptimes):
    uptimes_dep = all_dep_uptimes[dep_num]
    all_other_uptimes = [all_dep_uptimes[i] for i in range(len(all_dep_uptimes)) if dep_num != i]
    overlaps_list = []
    for other_uptimes_dep in all_other_uptimes:
        covering_time = 0
        for uptime_dep in uptimes_dep:
            for other_uptime_dep in other_uptimes_dep:
                overlap = min(uptime_dep[0] + time_awoken, other_uptime_dep[0] + time_awoken) - max(uptime_dep[0], other_uptime_dep[0])
                covering_time += overlap if overlap > 0 else 0

        percentage_overlap = covering_time/(time_awoken*freq)
        overlaps_list.append(percentage_overlap)

    return overlaps_list


if __name__ == "__main__":
    file_name = sys.argv[1]
    output = json.load(open(file_name))

    # for i in range(len(output[0])):
    #     print(f"FREQ: {i} ------------------")
    #     for j in range(len(output)):
    #         print(output[j][i], end="")
    #     print("-----------------")
    print(file_name)
    for i in range(len(output[0])):
        print(f"--- FREQ: {i} -----")
        for k in range(1, len(output)):
            o0, d0 = output[0][i]
            o2, d2 = output[k][i]
            print(output[0][i], end="")
            print(output[k][i], end="")
            print(f"   Server/dep{k-1}   Overlap: {max(min(o0+d0, o2+d2) - max(o0, o2), 0)}")
        print("-----------------\n")

    dep_num = 0  # Check only server
    cov_perc_list = compute_covering_time_dep(dep_num, 60, 30, output)
    server_means_coverage = round(sum(cov_perc_list) / len(cov_perc_list), 2)

    print(server_means_coverage)
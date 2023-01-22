import json

transitions_times_0 = json.load(open("../parameters/transitions_times/transitions_times-1-30-deps12-0.json"))["transitions_times"]
transitions_times_1 = json.load(open("../parameters/transitions_times/transitions_times-1-30-deps12-1.json"))["transitions_times"]

def _get_transitions_times(transitions_times_dict):
    t_sa_1 = transitions_times_dict["server"]["t_sa"]
    t_sc_1 = transitions_times_dict["server"]["t_sc"]
    t_sr_1 = transitions_times_dict["server"]["t_sr"]
    t_ss_1 = transitions_times_dict["server"]["t_ss"]
    t_sp_1 = transitions_times_dict["server"]["t_sp"]

    t_dis_1 = [k["t_di"] for n, k in transitions_times_dict.items() if n != "server"]
    t_drs_1 = [k["t_dr"] for n, k in transitions_times_dict.items() if n != "server"]
    t_dus_1 = [k["t_du"] for n, k in transitions_times_dict.items() if n != "server"]

    return t_sa_1, t_sc_1, t_sr_1, t_ss_1, t_sp_1, t_dis_1, t_drs_1, t_dus_1


def compute_theoretical_100_max_deploy_time(transitions_times_dict):
    t_sa_1, t_sc_1, t_sr_1, t_ss_1, t_sp_1, t_dis_1, t_drs_1, t_dus_1 = _get_transitions_times(transitions_times_dict)
    first_sync_time = 0
    index_f = -1
    for i in range(12):
        u = max(t_sa_1, t_dis_1[i]) + t_sc_1[i]
        if u > first_sync_time:
            first_sync_time = u
            index_f = i

    # print(first_sync_time, index_f)

    second_sync_time = 0
    index_s = -1
    for i in range(12):
        v = max(t_dis_1[i] + t_drs_1[i], first_sync_time + t_sr_1)
        if v > second_sync_time:
            second_sync_time = v
            index_s = i

    # print(second_sync_time, index_s)

    return second_sync_time, index_s

def compute_theoretical_100_max_update_time(transitions_times_dict):
    t_sa_1, t_sc_1, t_sr_1, t_ss_1, t_sp_1, t_dis_1, t_drs_1, t_dus_1 = _get_transitions_times(transitions_times_dict)
    first_sync_time = 0
    index_s = -1
    for i in range(12):
        u = t_ss_1[i] + max(t_dus_1[i] + t_drs_1[i], t_sp_1[i] + t_sr_1)
        if u > first_sync_time:
            first_sync_time = u
            index_s = i

    print(first_sync_time, index_s)

    end_reconf = first_sync_time
    return end_reconf, index_s

t_sa_0, t_sc_0, t_sr_0, t_ss_0, t_sp_0, t_dis_0, t_drs_0, t_dus_0 = _get_transitions_times(transitions_times_0)
server_suspend_time_T0 = max([t_ss_0[i] + t_sp_0[i] for i in range(12)])
print(server_suspend_time_T0)

t_sa_1, t_sc_1, t_sr_1, t_ss_1, t_sp_1, t_dis_1, t_drs_1, t_dus_1 = _get_transitions_times(transitions_times_1)
server_suspend_time_T1 = max([t_ss_1[i] + t_sp_1[i] for i in range(12)])
print(server_suspend_time_T1)


T0_100_max_deploy_time, index_deploy_T0 = compute_theoretical_100_max_deploy_time(transitions_times_0)
T0_100_max_update_time, index_update_T0 = compute_theoretical_100_max_update_time(transitions_times_0)

print(f"T0_100_max_deploy_time: {T0_100_max_deploy_time}")
print(f"T0_100_max_update_time: {T0_100_max_update_time}")

T1_100_max_deploy_time, index_deploy_T1 = compute_theoretical_100_max_deploy_time(transitions_times_1)
T1_100_max_update_time, index_update_T1 = compute_theoretical_100_max_update_time(transitions_times_1)

print(f"T1_100_max_deploy_time: {T1_100_max_deploy_time}")
print(f"T1_100_max_update_time: {T1_100_max_update_time}")

import json


class AssertionsSynchronous:
    class perc_100:
        # max_deploy_duration      = max(max(t_sa, t_di) + t_sc_i) + t_sr
        # min_deploy_duration      = min(t_di + t_dr)
        # max_deploy_sync_duration = max_deploy_duration - overflow - min_deploy_duration
        # max_update_duration      = max(t_ss_i + max(t_sp_i, max(t_du_j + t_dr_j)) + t_sr)
        # min_update_duration      = min(t_ss_i + t_du_i + t_dr_i)
        # max_update_sync_duration = max_update_duration - overflow - min_update_duration
        class T0:
            def assert_synchronous_100_perc_T0_deploy(self):
                #     = t_sc_1 + t_di_1 + t_sr
                #     = 34.59
                res = (14.07 + 19.12) + 1.4
                return


            def assert_synchronous_100_perc_T0_deploy_sync(self):
                # res = max_deploy_duration (server) - overflow_sleeping (server) - min_deploy_duration (dep5)
                #     = 28.6
                res = 34.59 - 3.19 - 2.8
                return


            def assert_synchronous_100_perc_T0_update(self):
                # res = max(t_ss_i + max(t_du_i + t_sp_i) + max(t_dr_i, t_sr)) + t_sr
                #     = 20.55
                res = 1.07 + 13.8 + 4.28 + 1.4
                return

            # zip(t_ss, t_sp, t_dus, t_drs)

            def assert_synchronous_100_perc_T0_update_sync(self):
                # res = max_update_duration (server) - overflow_sleeping (server) - min_update_duration (dep8)
                #     = 17.13
                res = 19.48 - 0 - 2.35
                return

        # Sleeping: 30
        # Sleeping sync: 34

        class T1:
            def assert_synchronous_100_perc_T1_deploy(self):
                #     = t_sc_3 + t_di_3 + t_sr
                #     = 26.66
                res = 9.82 + 6.33 + 10.51
                return


            def assert_synchronous_100_perc_T1_deploy_sync(self):
                #     = 22.26
                res = 26.66 - 0 - 2.4
                return


            def assert_synchronous_100_perc_T1_update(self):
                #     = 35.32  # TODO: calcul à revoir
                res = max_update_duration_100_T1  # TODO: calcul à revoir
                return

            # zip(t_ss, t_sp, t_dus, t_drs)

            def assert_synchronous_100_perc_T1_update_sync(self):
                #     = 33.55
                res = 38.17 - 0 - 4.62
                return

            # Sleeping: 35
            # Sleeping sync: 35


transitions_times_0 = json.load(open("../parameters/transitions_times/transitions_times-1-30-deps12-0.json"))["transitions_times"]
transitions_times_1 = json.load(open("../parameters/transitions_times/transitions_times-1-30-deps12-1.json"))["transitions_times"]


t_sa_0 = transitions_times_0["server"]["t_sa"]
t_sc_0 = transitions_times_0["server"]["t_sc"]
t_sr_0 = transitions_times_0["server"]["t_sr"]
t_ss_0 = transitions_times_0["server"]["t_ss"]
t_sp_0 = transitions_times_0["server"]["t_sp"]

t_sa_1 = transitions_times_1["server"]["t_sa"]
t_sc_1 = transitions_times_1["server"]["t_sc"]
t_sr_1 = transitions_times_1["server"]["t_sr"]
t_ss_1 = transitions_times_1["server"]["t_ss"]
t_sp_1 = transitions_times_1["server"]["t_sp"]

t_dis_1 = [k["t_di"] for n, k in transitions_times_1.items() if n != "server"]
t_drs_1 = [k["t_dr"] for n, k in transitions_times_1.items() if n != "server"]
t_dus_1 = [k["t_du"] for n, k in transitions_times_1.items() if n != "server"]

# max_du_dr = max([t_dus_1[i] + t_drs_1[i] for i in range(12)])
# max_update_duration_100_T1 = max([t_ss_1[i] + max(t_sp_1[i], max_du_dr) + t_sr_1 for i in range(12)])   OLD
max_update_duration_100_T1 = max([t_ss_1[i] + max(t_sp_1[i], t_dus_1[i] + t_drs_1[i]) + t_sr_1 for i in range(12)])
min_update_duration_100_T1 = min([t_ss_1[i] + t_dus_1[i] + t_drs_1[i] for i in range(12)])
max_waitall_True_duration = max([t_ss_1[i] + t_dus_1[i] + t_drs_1[i] for i in range(12)])
print(max_update_duration_100_T1)
# print(max_waitall_True_duration)
#
# for i in range(12):
#     print(i, t_ss_1[i] + t_dus_1[i] + t_drs_1[i])


# for i in range(12):
#     print(t_ss_1[i] + max(t_sp_1[i], t_dus_1[i] + t_drs_1[i]))

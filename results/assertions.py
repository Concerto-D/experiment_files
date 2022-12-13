class AssertionsSynchronous:
    def assert_synchronous_100_perc_T0_deploy(self):
        # res = t_sa + max(t_sc_i + t_di_i) + t_sr
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


    def assert_synchronous_100_perc_T0_reconf(self):
        # res = max_deploy_duration + max_update_duration
        return


    def assert_synchronous_100_perc_T0_reconf_sync(self):
        # res = max_deploy_sync_duration + max_update_sync_duration
        return


    def assert_synchronous_100_perc_T0_sleeping(self):
        # res = max(sum_j_deploy_update(round_reconf_i + sleeping_time_i))
        #     = 34
        return


    def assert_synchronous_100_perc_T0_sleeping_sync(self):
        # res = max_deploy_sync_duration + max_update_sync_duration
        #     = 0
        return

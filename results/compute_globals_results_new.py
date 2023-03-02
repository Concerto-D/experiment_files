import copy
import os
import numpy as np
import yaml

output_trans = {
    "T0": {
        "global_finished_reconf": [],
        "max_deploy_time": [],
        "max_update_time": [],
        "max_reconf_time": [],
        "max_sleeping_time": [],
        "max_execution_time": []
    },
    "T1": {
        "global_finished_reconf": [],
        "max_deploy_time": [],
        "max_update_time": [],
        "max_reconf_time": [],
        "max_sleeping_time": [],
        "max_execution_time": []
    }
}

output = {
    "tab1": {
        "2-2": {
            "mjuz-2-comps": copy.deepcopy(output_trans),
            "synchronous": copy.deepcopy(output_trans),
            "asynchronous": copy.deepcopy(output_trans)
        },
        "25-35": {
            "mjuz-2-comps": copy.deepcopy(output_trans),
            "synchronous": copy.deepcopy(output_trans),
            "asynchronous": copy.deepcopy(output_trans)
        },
        "50-50": {
            "mjuz-2-comps": copy.deepcopy(output_trans),
            "synchronous": copy.deepcopy(output_trans),
            "asynchronous": copy.deepcopy(output_trans)
        },
        "1-1": {
            "mjuz-2-comps": copy.deepcopy(output_trans),
            "synchronous": copy.deepcopy(output_trans),
            "asynchronous": copy.deepcopy(output_trans)
        }
    },
    "tab2": {
        "2-2": {
            "0": copy.deepcopy(output_trans),
            "0.5": copy.deepcopy(output_trans),
            "1": copy.deepcopy(output_trans),
        },
        "25-35": {
            "0": copy.deepcopy(output_trans),
            "0.5": copy.deepcopy(output_trans),
            "1": copy.deepcopy(output_trans),
        },
        "50-50": {
            "0": copy.deepcopy(output_trans),
            "0.5": copy.deepcopy(output_trans),
            "1": copy.deepcopy(output_trans),
        },
        "1-1": {
            "0": copy.deepcopy(output_trans),
            "0.5": copy.deepcopy(output_trans),
            "1": copy.deepcopy(output_trans),
        }
    }
}

excluded_files_name = [
    "global_results_expes.yaml",
    "global_results_expes_computed.yaml",
    "old_global_results_expes.yaml",
    "old_global_results_expes_computed.yaml",
]
def main(results_dir):
    for file_name in os.listdir(results_dir):
        if os.path.isdir(results_dir + "/" + file_name) or file_name in excluded_files_name:
            continue

        with open(f"{results_dir}/{file_name}") as f:
            file_content = yaml.safe_load(f)
        # TODO: change percs (2-2 for 0_02-0_02)
        if "0_02-0_05" in file_content["expe_parameters"]["uptimes_file_name"] or "0_02-0_02" in file_content["expe_parameters"]["uptimes_file_name"]:
            perc_name = "2-2"
        elif "0_2-0_3" in file_content["expe_parameters"]["uptimes_file_name"] or "0_25-0_25" in file_content["expe_parameters"]["uptimes_file_name"]:
            perc_name = "25-35"
        elif "0_5-0_6" in file_content["expe_parameters"]["uptimes_file_name"] or "0_5-0_5" in file_content["expe_parameters"]["uptimes_file_name"]:
            perc_name = "50-50"
        else:
            perc_name = "1-1"

        if "-0.json" in file_content["expe_parameters"]["transitions_times_file_name"]:
            t_name = "T0"
        else:
            t_name = "T1"

        tab_name = "tab1" if file_content["expe_parameters"]["waiting_rate"] == 1 else "tab2"
        if tab_name == "tab1":
            version_name = file_content["expe_parameters"]["version_concerto_name"]
        else:
            version_name = str(file_content["expe_parameters"]["waiting_rate"])

        global_results = file_content["global_results"]

        for key, value in global_results.items():
            output[tab_name][perc_name][version_name][t_name][key].append(value)

        if "files" not in output[tab_name][perc_name][version_name][t_name]:
            output[tab_name][perc_name][version_name][t_name]["files"] = [file_name]
        else:
            output[tab_name][perc_name][version_name][t_name]["files"].append(file_name)

    with open(f"{results_dir}/global_results_expes.yaml", "w") as f:
        yaml.safe_dump(output, f, indent=4)

    compute_mean_std(results_dir, output)


def compute_mean_std(results_dir, output):
    computed_output = copy.deepcopy(output)
    for tab, tab_values in output.items():
        for perc, perc_values in tab_values.items():
            for categ, categ_values in perc_values.items():
                for trans, trans_values in categ_values.items():
                    for metric, metric_values in trans_values.items():
                        need_to_report_to_tab2 = tab == "tab1" and perc != "1-1" and categ == "asynchronous"
                        if metric not in ["global_finished_reconf", "files"] and len(metric_values) > 0:
                            c_mean = np.mean(metric_values)
                            c_std = np.std(metric_values)
                            computed_output[tab][perc][categ][trans][metric] = {
                                "mean": str(round(float(c_mean), 2)).replace(".", ","),
                                "std": str(round(float(c_std), 2)).replace(".", ",")
                            }

                            if need_to_report_to_tab2:
                                computed_output["tab2"][perc]["1"][trans][metric] = copy.deepcopy(computed_output[tab][perc][categ][trans][metric])
                        else:
                            if need_to_report_to_tab2:
                                computed_output["tab2"][perc]["1"][trans][metric] = copy.deepcopy(metric_values)

    with open(f"{results_dir}/global_results_expes_computed.yaml", "w") as f:
        yaml.safe_dump(computed_output, f, indent=4)


if __name__ == "__main__":
    for n in ["asynchronous", "synchronous", "mjuz"]:
        main(f"/home/aomond/experiments_results/concerto-d/prod/raspberry-5_deps-50-duration/{n}")

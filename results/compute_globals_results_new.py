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
        "2-5": {
            "synchronous": copy.deepcopy(output_trans),
            "asynchronous": copy.deepcopy(output_trans)
        },
        "20-30": {
            "synchronous": copy.deepcopy(output_trans),
            "asynchronous": copy.deepcopy(output_trans)
        },
        "50-60": {
            "synchronous": copy.deepcopy(output_trans),
            "asynchronous": copy.deepcopy(output_trans)
        },
        "1-1": {
            "synchronous": copy.deepcopy(output_trans),
            "asynchronous": copy.deepcopy(output_trans)
        }
    },
    "tab2": {
        "2-5": {
            "0": copy.deepcopy(output_trans),
            "0.5": copy.deepcopy(output_trans),
            "1": copy.deepcopy(output_trans),
        },
        "20-30": {
            "0": copy.deepcopy(output_trans),
            "0.5": copy.deepcopy(output_trans),
            "1": copy.deepcopy(output_trans),
        },
        "50-60": {
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


def main(results_dir):
    for file_name in os.listdir(results_dir):
        if os.path.isdir(results_dir + "/" + file_name):
            continue

        with open(f"{results_dir}/{file_name}") as f:
            file_content = yaml.safe_load(f)
        if "0_02-0_05" in file_content["expe_parameters"]["uptimes_file_name"]:
            perc_name = "2-5"
        elif "0_2-0_3" in file_content["expe_parameters"]["uptimes_file_name"]:
            perc_name = "20-30"
        elif "0_5-0_6" in file_content["expe_parameters"]["uptimes_file_name"]:
            perc_name = "50-60"
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
                        if metric not in ["global_finished_reconf", "files"] and len(metric_values) > 0:
                            c_mean = np.mean(metric_values)
                            c_std = np.std(metric_values)
                            computed_output[tab][perc][categ][trans][metric] = {
                                "mean": str(round(float(c_mean), 2)).replace(".", ","),
                                "std": str(round(float(c_std), 2)).replace(".", ",")
                            }

                            # Visualisation des std supérieures à 1
                            resulted_std = computed_output[tab][perc][categ][trans][metric]["std"]
                            if c_std > 1:
                                computed_output[tab][perc][categ][trans][metric]["std"] += f"     # STD == {resulted_std}"

    with open(f"{results_dir}/global_results_expes_computed.yaml", "w") as f:
        yaml.safe_dump(computed_output, f, indent=4)


if __name__ == "__main__":
    main("/home/aomond/experiments_results/concerto-d/prod/raspberry-5_deps-no-conn-synced/synchrone")

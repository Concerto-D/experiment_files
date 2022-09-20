import copy
import json
import os
import numpy as np

output_trans = {
    "T0": {
        "finished_reconf": [],
        "max_deploy_time": [],
        "max_update_time": [],
        "max_reconf_time": [],
        "max_sleeping_time": [],
        "max_execution_time": []
    },
    "T1": {
        "finished_reconf": [],
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
            "timeout0": copy.deepcopy(output_trans),
            "timeout50": copy.deepcopy(output_trans)
        },
        "20-30": {
            "timeout0": copy.deepcopy(output_trans),
            "timeout50": copy.deepcopy(output_trans)
        },
        "50-60": {
            "timeout0": copy.deepcopy(output_trans),
            "timeout50": copy.deepcopy(output_trans)
        },
    }
}


def get_global_results(file_content):
    results = file_content["results"]
    max_deploy_values = max(results.values(), key=lambda values: values["total_deploy_duration"])
    max_deploy_time = max_deploy_values["total_deploy_duration"]

    max_update_values = max(results.values(), key=lambda values: values["total_update_duration"])
    max_update_time = max_update_values["total_update_duration"]

    max_reconf_values = max(results.values(), key=lambda values: values["total_deploy_duration"] + values["total_update_duration"])
    max_reconf_time = max_reconf_values["total_deploy_duration"] + max_reconf_values["total_update_duration"]

    max_sleeping_values = max(results.values(), key=lambda values: values["total_sleeping_time"])
    max_sleeping_time = max_sleeping_values["total_sleeping_time"]

    max_execution_values = max(results.values(), key=lambda values: values["total_sleeping_time"] + values["total_uptime_duration"])
    max_execution_time = max_execution_values["total_sleeping_time"] + max_execution_values["total_uptime_duration"]

    # if "global_results" not in file_content.keys():
    #     finished_reconf = "Skipped"
    # else:
    #     finished_reconf = file_content["global_results"]["finished_reconf"]

    return {
        "finished_reconf": file_content["global_results"]["finished_reconf"],
        "max_deploy_time": round(max_deploy_time, 2),
        "max_update_time": round(max_update_time, 2),
        "max_reconf_time": round(max_reconf_time, 2),
        "max_sleeping_time": round(max_sleeping_time, 2),
        "max_execution_time": round(max_execution_time, 2),
    }


def main():
    dir = "../../experiment-expe-replay-async-expes-dir"
    for dir_name in os.listdir(dir):
        print(dir_name)
        for file_name in os.listdir(f"{dir}/{dir_name}"):
            if "results_" in file_name:
                with open(f"{dir}/{dir_name}/{file_name}") as f:
                    file_content = json.load(f)
                if "0_02-0_05" in file_content["parameters"]["uptimes_file_name"]:
                    perc_name = "2-5"
                elif "0_2-0_3" in file_content["parameters"]["uptimes_file_name"]:
                    perc_name = "20-30"
                elif "0_5-0_6" in file_content["parameters"]["uptimes_file_name"]:
                    perc_name = "50-60"
                else:
                    perc_name = "1-1"

                if "-0.json" in file_content["parameters"]["transitions_times_file_name"]:
                    t_name = "T0"
                else:
                    t_name = "T1"

                tab_name = "tab1" if file_content["parameters"]["waiting_rate"] == 1 else "tab2"
                if tab_name == "tab1":
                    version_name = file_content["parameters"]["version_concerto_name"]
                else:
                    version_name = "timeout0" if file_content["parameters"]["waiting_rate"] == 0 else "timeout50"
                # global_results = file_content["global_results"]
                global_results = get_global_results(file_content)

                for key, value in global_results.items():
                    output[tab_name][perc_name][version_name][t_name][key].append(value)

                to_s = f"{dir_name}/{file_name}"
                if "files" not in output[tab_name][perc_name][version_name][t_name]:
                    output[tab_name][perc_name][version_name][t_name]["files"] = [to_s]
                else:
                    output[tab_name][perc_name][version_name][t_name]["files"].append(to_s)

    with open(f"{dir}/global_results_expes.json", "w") as f:
        json.dump(output, f, indent=4)

    compute_mean_std(dir, output)


def compute_mean_std(dir, output):
    computed_output = copy.deepcopy(output)
    for tab, tab_values in output.items():
        for perc, perc_values in tab_values.items():
            for categ, categ_values in perc_values.items():
                for trans, trans_values in categ_values.items():
                    for metric, metric_values in trans_values.items():
                        if metric not in ["finished_reconf", "files"] and len(metric_values) > 0:
                            c_mean = np.mean(metric_values)
                            c_std = np.std(metric_values)
                            computed_output[tab][perc][categ][trans][metric] = {
                                "mean": round(c_mean, 3),
                                "std": round(c_std, 3)
                            }

    with open(f"{dir}/global_results_expes_computed.json", "w") as f:
        json.dump(computed_output, f, indent=4)


if __name__ == "__main__":
    main()
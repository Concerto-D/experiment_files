import copy
import json
import os

output_trans = {
    "T0": {
        "finished_reconf": [],
        "deploy": [],
        "update": [],
        "max_uptime": [],
        "max_sleeping": [],
        "max_reconf": []
    },
    "T1": {
        "finished_reconf": [],
        "deploy": [],
        "update": [],
        "max_uptime": [],
        "max_sleeping": [],
        "max_reconf": []
    }
}

output = {
    "tab1": {
        "2-5": {
            "sync": copy.deepcopy(output_trans),
            "async": copy.deepcopy(output_trans)
        },
        "20-30": {
            "sync": copy.deepcopy(output_trans),
            "async": copy.deepcopy(output_trans)
        },
        "50-60": {
            "sync": copy.deepcopy(output_trans),
            "async": copy.deepcopy(output_trans)
        },
        "1-1": {
            "sync": copy.deepcopy(output_trans),
            "async": copy.deepcopy(output_trans)
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

    if "global_results" not in file_content.keys():
        finished_reconf = "Skipped"
    else:
        finished_reconf = file_content["global_results"]["finished_reconf"]

    return {
        "finished_reconf": finished_reconf,
        "deploy": round(max_deploy_time, 2),
        "update": round(max_update_time, 2),
        "max_uptime": round(max_reconf_time, 2),
        "max_sleeping": round(max_sleeping_time, 2),
        "max_reconf": round(max_execution_time, 2),
    }


for dir_name in os.listdir("to_analyse"):
    print(dir_name)
    for file_name in os.listdir(f"to_analyse/{dir_name}"):
        if "finished_reconfiguration" not in file_name:
            with open(f"to_analyse/{dir_name}/{file_name}") as f:
                file_content = json.load(f)

            if "perc-2-5" in file_name:
                perc_name = "2-5"
            elif "perc-20-30" in file_name:
                perc_name = "20-30"
            elif "perc-50-60" in file_name:
                perc_name = "50-60"
            else:
                perc_name = "1-1"

            if "T0" in file_name:
                t_name = "T0"
            else:
                t_name = "T1"

            to_s = f"{dir_name}/{file_name}"
            if "expe_1" in file_name:
                tab_name = "tab1"
                version_name = "async" if "asynchrone" in file_name else "sync"
                global_results = get_global_results(file_content)
                for key, value in global_results.items():
                    output[tab_name][perc_name][version_name][t_name][key].append(value)
                if "files" not in output[tab_name][perc_name][version_name][t_name]:
                    output[tab_name][perc_name][version_name][t_name]["files"] = [to_s]
                else:
                    output[tab_name][perc_name][version_name][t_name]["files"].append(to_s)

            else:
                tab_name = "tab2"
                version_name = "timeout0" if ("expe_2" in file_name and ("timeout" not in file_name or "timeout-False" in file_name)) else "timeout50"
                global_results = get_global_results(file_content)
                for key, value in global_results.items():
                    output[tab_name][perc_name][version_name][t_name][key].append(value)
                if "files" not in output[tab_name][perc_name][version_name][t_name]:
                    output[tab_name][perc_name][version_name][t_name]["files"] = [to_s]
                else:
                    output[tab_name][perc_name][version_name][t_name]["files"].append(to_s)


with open("global_results.json", "w") as f:
    json.dump(output, f, indent=4)
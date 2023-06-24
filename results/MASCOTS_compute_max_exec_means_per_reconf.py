import os
import yaml
import numpy as np

def compute_max_exec_duration(details_assemblies_results, reconf_name):
    max_exec = max(details_assemblies_results.values(), key=lambda values: values[reconf_name]["total_event_uptime_duration"] + values[reconf_name]["total_event_sleeping_duration"])
    return max_exec[reconf_name]["total_event_uptime_duration"] + max_exec[reconf_name]["total_event_sleeping_duration"]


for version in ["asynchronous", "synchronous", "mjuz"]:
    global_results_means = {}

    # Creation du dict avec les résultats pour le max exec
    # async_results_dir = f"/home/aomond/experiments_results/concerto-d/prod/mascots/{version}"
    async_results_dir = f"mascots_2023/{version}"
    for entry_name in os.listdir(async_results_dir):
        abs_entry_path = f"{async_results_dir}/{entry_name}"
        if not os.path.isdir(abs_entry_path):
            results = yaml.safe_load(open(abs_entry_path, "r"))

            version_concerto_name = results["expe_parameters"]["version_concerto_name"]
            transitions_times_file_name = results["expe_parameters"]["transitions_times_file_name"]
            uptimes_file_name = results["expe_parameters"]["uptimes_file_name"]

            for reconf_name in ["deploy", "update"]:
                key = (version_concerto_name, uptimes_file_name, transitions_times_file_name, reconf_name)

                if version == "mjuz":
                    max_exec = results["details_assemblies_results"]["server"][reconf_name]["total_event_uptime_duration"] + results["details_assemblies_results"]["server"][reconf_name]["total_event_sleeping_duration"]
                else:
                    max_exec = compute_max_exec_duration(results["details_assemblies_results"], reconf_name)

                if key not in global_results_means.keys():
                    global_results_means[key] = {"results": [[max_exec], [entry_name]]}
                else:
                    global_results_means[key]["results"][0].append(max_exec)
                    global_results_means[key]["results"][1].append(entry_name)


    # Ajout des moyennes au dict
    for k,v in global_results_means.items():
        if version not in k[0]:
            continue
        if k[1] in ["mascots_uptimes-60-50-5-ud0_od1_15_25_perc.json", "mascots_uptimes-60-50-5-ud0_od2_15_25_perc.json"]:
            continue
        c_mean = np.mean(v["results"][0])
        c_std = np.std(v["results"][0])
        c_std_perc = c_std*100/c_mean
        global_results_means[k]["mean"] = str(round(c_mean, 2)).replace(".", ",")
        global_results_means[k]["std"] = str(round(c_std, 2)).replace(".", ",")
        global_results_means[k]["std_perc"] = str(round(c_std_perc, 2)).replace(".", ",")
        # print(v["results"])
        pretty_key = f"{k[0]} - {k[1].split('-')[-1]} - {'T0' if '-0' in k[2] else 'T1'} {k[3]}"
        print(f"{pretty_key}: {v['mean']} {v['std']} {v['std_perc']}% - {len(v['results'][0])} executions")
        # print()
        # print(v["std"])
    print()

    # Comparison duration


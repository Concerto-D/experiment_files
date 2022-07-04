import json
import os
import sys

path = "." if len(sys.argv) < 2 else sys.argv[1]

for f in os.listdir(path):
    if "asynchrone" in f or "synchrone" in f:
        with open(f"{path}/{f}") as fi:
            output = json.load(fi)

        results = output["results"]
        max_deploy_values = max(results.values(), key=lambda values: values["total_deploy_duration"])
        max_deploy_time = max_deploy_values["total_deploy_duration"]

        max_update_values = max(results.values(), key=lambda values: values["total_update_duration"])
        max_update_time = max_update_values["total_update_duration"]

        max_reconf_time = max_deploy_time + max_update_time

        max_sleeping_values = max(results.values(), key=lambda values: values["total_sleeping_time"])
        max_sleeping_time = max_sleeping_values["total_sleeping_time"]

        max_execution_values = max(results.values(), key=lambda values: values["total_sleeping_time"] + values["total_uptime_duration"])
        max_execution_time = max_execution_values["total_sleeping_time"] + max_execution_values["total_uptime_duration"]

        print(json.dumps({
            "file_name": f"{path}/{f}",
            "max_deploy_time": round(max_deploy_time, 2),
            "max_update_time": round(max_update_time, 2),
            "max_reconf_time": round(max_reconf_time, 2),
            "max_sleeping_time": round(max_sleeping_time, 2),
            "max_execution_time": round(max_execution_time, 2),
        }, indent=4))
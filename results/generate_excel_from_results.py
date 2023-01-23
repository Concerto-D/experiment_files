import yaml
from openpyxl import Workbook

case_mapping = {
    ("2-5", "synchronous", "T0", "max_deploy_time"): "C5",
    ("2-5", "synchronous", "T0", "max_update_time"): "C6",
    ("2-5", "synchronous", "T1", "max_deploy_time"): "C8",
    ("2-5", "synchronous", "T1", "max_update_time"): "C9",
    ("2-5", "synchronous", "T1", "max_update_time"): "C9",
    ("2-5", "synchronous", "T0", "global_finished_reconf"): "C20",
    ("2-5", "synchronous", "T0", "files"): "C21",
    ("2-5", "synchronous", "T1", "global_finished_reconf"): "C22",
    ("2-5", "synchronous", "T1", "files"): "C23",

    ("20-30", "synchronous", "T0", "max_deploy_time"): "F5",
    ("20-30", "synchronous", "T0", "max_update_time"): "F6",
    ("20-30", "synchronous", "T1", "max_deploy_time"): "F8",
    ("20-30", "synchronous", "T1", "max_update_time"): "F9",
    ("20-30", "synchronous", "T0", "global_finished_reconf"): "F20",
    ("20-30", "synchronous", "T0", "files"): "F21",
    ("20-30", "synchronous", "T1", "global_finished_reconf"): "F22",
    ("20-30", "synchronous", "T1", "files"): "F23",

    ("50-60", "synchronous", "T0", "max_deploy_time"): "I5",
    ("50-60", "synchronous", "T0", "max_update_time"): "I6",
    ("50-60", "synchronous", "T1", "max_deploy_time"): "I8",
    ("50-60", "synchronous", "T1", "max_update_time"): "I9",
    ("50-60", "synchronous", "T0", "global_finished_reconf"): "I20",
    ("50-60", "synchronous", "T0", "files"): "I21",
    ("50-60", "synchronous", "T1", "global_finished_reconf"): "I22",
    ("50-60", "synchronous", "T1", "files"): "I23",

    ("1-1", "synchronous", "T0", "max_deploy_time"): "L5",
    ("1-1", "synchronous", "T0", "max_update_time"): "L6",
    ("1-1", "synchronous", "T1", "max_deploy_time"): "L8",
    ("1-1", "synchronous", "T1", "max_update_time"): "L9",
    ("1-1", "synchronous", "T0", "global_finished_reconf"): "L20",
    ("1-1", "synchronous", "T0", "files"): "L21",
    ("1-1", "synchronous", "T1", "global_finished_reconf"): "L22",
    ("1-1", "synchronous", "T1", "files"): "L23",
}


def generate_table_1(data_path):
    wb = Workbook()

    # grab the active worksheet
    ws = wb.active

    # Titles
    ws["A4"] = "DEPLOY"
    ws["A5"] = "T0"
    ws["A6"] = "T1"
    ws["A7"] = "UPDATE"
    ws["A8"] = "T0"
    ws["A9"] = "T1"
    ws["B3"] = "Mjuz"
    ws["C3"] = "Sync"
    ws["D3"] = "Async"
    ws["E3"] = "Mjuz"
    ws["F3"] = "Sync"
    ws["G3"] = "Async"
    ws["H3"] = "Mjuz"
    ws["I3"] = "Sync"
    ws["J3"] = "Async"
    ws["K3"] = "Mjuz"
    ws["L3"] = "Sync"
    ws["M3"] = "Async"
    ws["B2"] = "2-5%"
    ws["E2"] = "20-30%"
    ws["H2"] = "50-60%"
    ws["K2"] = "100%"

    # Put results
    with open(data_path) as f:
        tab_values = yaml.safe_load(f)["tab1"]

    # Refacto avec compute_globals_results_new.py
    for perc, perc_values in tab_values.items():
        for categ, categ_values in perc_values.items():
            for trans, trans_values in categ_values.items():
                for metric, metric_values in trans_values.items():
                    if len(metric_values) > 0:
                        mapped_case = case_mapping.get((perc, categ, trans, metric))
                        if mapped_case is not None:
                            col = mapped_case[0]
                            lig = int(mapped_case[1:])

                            if metric == "global_finished_reconf":
                                ws[mapped_case] = all(metric_values)
                            elif metric == "files":
                                ws[mapped_case] = len(metric_values)
                            else:
                                ws[mapped_case] = metric_values["mean"]
                                ws[col+str(lig+8)] = metric_values["std"]

    # Save the file
    wb.save("table1.xlsx")

generate_table_1("/home/aomond/experiments_results/concerto-d/prod/raspberry-5_deps-no-conn-synced/synchrone/global_results_expes_computed.yaml")

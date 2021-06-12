"""
+--------------------------------------+
| Usage                                |
| see tal/trials/blip-player/07/run.sh |
+--------------------------------------+
"""

import os
import sys
import csv
from common_py_functions import now_2_epochms

g_tx_label = {"-":"_"}

print("digraph G {")
print("node [fontname=\"courier\"];")

with open('/dev/stdin', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        requestor = row['requestor']
        responder = row['responder']
        tx_id     = row['tx-id']
        p_tx_id   = row['parent-tx-id']
        rcvd_at   = row['received-at']
        fnx_name  = row['if-fnx-name']

        if not tx_id in g_tx_label:
            label_name = tx_id.replace("-","_")
            g_tx_label[tx_id] = label_name
            p_label_name = g_tx_label[p_tx_id]

            print(f"{label_name} [shape=Mrecord," +\
                  f"label=\"{{{label_name}|{requestor}" +\
                  f" \> ({fnx_name}) \> {responder}|{rcvd_at}}}\"]")

            print(f"{p_label_name} -> {label_name};")

print("}")


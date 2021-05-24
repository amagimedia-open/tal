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

g_delimiter   = ":"
g_root_tx     = '-'
g_root_folder = f"txtree-{now_2_epochms()}"
g_tx_info     = {g_root_tx: g_root_folder}
g_tx_parent   = {g_root_tx:None}

def create_folder(path):
    os.system(f"mkdir {path}")
    #print(path, file=sys.stderr)
    #sys.stderr.flush()

def get_tx_path(tx_id):
    if (tx_id == '-'):
        return g_tx_info[tx_id]
    else:
        return f"{get_tx_path(g_tx_parent[tx_id])}/{g_tx_info[tx_id]}"

create_folder(g_root_folder)

with open('/dev/stdin', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        requestor = row['requestor']
        responder = row['responder']
        tx_id     = row['tx-id']
        p_tx_id   = row['parent-tx-id']
        rcvd_at   = row['received-at']
        fnx_name  = row['if-fnx-name']

        if not tx_id in g_tx_info:
            tx_info = (tx_id, str(rcvd_at), requestor, fnx_name, responder)
            g_tx_info[tx_id]   = g_delimiter.join(tx_info)
            g_tx_parent[tx_id] = p_tx_id
            create_folder(get_tx_path(tx_id))

os.system(f"tree --noreport {g_root_folder}")
os.system(f"rm -rf {g_root_folder}")


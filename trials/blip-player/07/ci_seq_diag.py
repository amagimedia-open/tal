"""
+--------------------------------------+
| Usage                                |
| see tal/trials/blip-player/07/run.sh |
+--------------------------------------+
"""

import os
import sys
import csv

g_delimiter   = ":"
g_root_tx     = '-'
g_tx_parent   = {g_root_tx:None}

def create_folder(path):
    os.system(f"mkdir {path}")
    #print(path, file=sys.stderr)
    #sys.stderr.flush()

def get_tx_path(tx_id):
    if (tx_id == '-'):
        return ""
    else:
        return f"{get_tx_path(g_tx_parent[tx_id])}/{tx_id}"

def get_comp_urls(filepath):

    comp_desc = {}

    with open(filepath, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            comp_name     = row["COMPONENT"]
            comp_desc_url = row["URL"]
            comp_desc[comp_name] = comp_desc_url

    return comp_desc

#----------------------------------------------------------------------------

if __name__ == "__main__":
    if (len(sys.argv) == 0):
        print("component description filepath not specified", file.sys.stderr)
        sys.exit(1)

comp_urls_filepath = sys.argv[1]
#print(f"comp_urls_filepath={comp_urls_filepath}", file=sys.stderr)
comp_urls = get_comp_urls(comp_urls_filepath)
#print(f"comp_urls={comp_urls}", file=sys.stderr)

print("@startuml")

with open('/dev/stdin', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        requestor = row['requestor']
        responder = row['responder']
        tx_id     = row['tx-id']
        p_tx_id   = row['parent-tx-id']
        rcvd_at   = row['received-at']
        fnx_name  = row['if-fnx-name']

        if not tx_id in g_tx_parent:
            g_tx_parent[tx_id] = p_tx_id

        req = (get_tx_path(tx_id), rcvd_at, fnx_name)
        req_str = g_delimiter.join(req)
        print(f"{requestor} -> {responder}: {req_str}")

for comp_name in comp_urls:
    print(f"url of {comp_name} is [[{comp_urls[comp_name]}]]")

print("@enduml")



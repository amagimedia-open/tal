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

#----------------------------------------------------------------------------

g_tx_label = {"-":"_"}
g_tx_node_template_filepath_env_var_name = "TAL_TX_NODE_TEMPLATE_FILEPATH"

#----------------------------------------------------------------------------

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

def replace_all(text, dic):

    for key in dic:
        text = text.replace(key, dic[key])

    return text

#----------------------------------------------------------------------------

def get_label_name(tx_id):

    return tx_id.replace("-","_")

#----------------------------------------------------------------------------

def gen_node_definition(tx_node_template_filepath, row, comp_urls):

    requestor = row['requestor']
    responder = row['responder']
    tx_id     = row['tx-id']
    p_tx_id   = row['parent-tx-id']
    rcvd_at   = row['received-at']
    fnx_name  = row['if-fnx-name']

    label_name = get_label_name(tx_id)

    replace_map  = {
        "__txidnodename__"  : label_name,
        "__txid__"          : tx_id,
        "__reqhref__"       : comp_urls[requestor],
        "__req__"           : requestor,
        "__fnx__"           : fnx_name,
        "__rsphref__"       : comp_urls[responder],
        "__rsp__"           : responder,
        "__rcvdat__"        : rcvd_at
    }

    node_defn_str = open(tx_node_template_filepath, 'r').read()
    node_defn_str = replace_all(node_defn_str, replace_map)

    return (label_name, node_defn_str)

#----------------------------------------------------------------------------

if __name__ == "__main__":
    if (len(sys.argv) == 0):
        print("component description filepath not specified", file.sys.stderr)
        sys.exit(1)

tx_node_template_filepath = os.environ[g_tx_node_template_filepath_env_var_name]
#print(f"template_filepath={tx_node_template_filepath}", file=sys.stderr)

comp_urls_filepath = sys.argv[1]
#print(f"comp_urls_filepath={comp_urls_filepath}", file=sys.stderr)
comp_urls = get_comp_urls(comp_urls_filepath)
#print(f"comp_urls={comp_urls}", file=sys.stderr)

print("digraph G {")

with open('/dev/stdin', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        tx_id     = row['tx-id']
        p_tx_id   = row['parent-tx-id']

        if not tx_id in g_tx_label:
            (label_name, node_defn_str) = \
                gen_node_definition(tx_node_template_filepath, row, comp_urls)
            g_tx_label[tx_id] = label_name
            p_label_name = g_tx_label[p_tx_id]

            print(node_defn_str)
            print(f"{p_label_name} -> {label_name};")
            print()

print("}")



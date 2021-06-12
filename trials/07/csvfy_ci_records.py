"""
+--------------------------------------+
| Usage                                |
| see tal/trials/blip-player/07/run.sh |
+--------------------------------------+
"""

import sys

g_max_cols  = 20
g_col_index = 0
g_col_names = {}
g_header_line_dumped = False

for line in sys.stdin:
    line = line.rstrip()
    #print(f"# {line}", file=sys.stderr)

    values = [""] * g_max_cols
    max_col_index = 0
    fields = line.split(',')

    for field in fields:
        (name,value) = field.split('=')

        if not name in g_col_names:
            g_col_names[name] = g_col_index
            g_col_index += 1

        col_index = g_col_names[name]
        if (max_col_index < col_index):
            max_col_index = col_index

        values[g_col_names[name]] = value

    if not g_header_line_dumped:
        print(','.join(list(g_col_names.keys())))
        g_header_line_dumped = True

    print(','.join(values[:max_col_index+1]))


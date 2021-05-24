#!/bin/bash

set -u

DIRNAME=$(readlink -e $(dirname $0))

source $TAL_VENV_ACTIVATE_FILE_PATH

python $DIRNAME/run.py run.py 2>/dev/null |\
python $DIRNAME/csvfy_ci_records.py |\
python $DIRNAME/tx_tree.py

set +u
deactivate


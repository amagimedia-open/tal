#!/bin/bash

set -u

DIRNAME=$(readlink -e $(dirname $0))

source $TAL_VENV_ACTIVATE_FILE_PATH

echo "#---[n_prod_1_cons_store]---"
python $DIRNAME/n_prod_1_cons_store.py

echo

echo "#---[n_prod_n_cons_store]---"
python $DIRNAME/n_prod_n_cons_store.py

set +u
deactivate


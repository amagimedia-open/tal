#!/bin/bash

set -u

DIRNAME=$(readlink -e $(dirname $0))

source $TAL_VENV_ACTIVATE_FILE_PATH

python $DIRNAME/run.py

set +u
deactivate


#!/bin/bash

set -u
#set -x

DIRNAME=$(readlink -e $(dirname $0))

source $TAL_VENV_ACTIVATE_FILE_PATH
cd $DIRNAME

python w3c_tc00_ut.py

set +u
deactivate

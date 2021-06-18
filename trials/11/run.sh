#!/bin/bash

set -u
#set -x

DIRNAME=$(readlink -e $(dirname $0))

source $TAL_VENV_ACTIVATE_FILE_PATH
cd $DIRNAME

#python -m unittest
#python -m unittest -v gen_trace_context.py
python gen_trace_context.py

set +u
deactivate

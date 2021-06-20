#!/bin/bash

set -u
#set -x

DIRNAME=$(readlink -e $(dirname $0))

source $TAL_VENV_ACTIVATE_FILE_PATH
cd $DIRNAME

python trace_context.py

set +u
deactivate

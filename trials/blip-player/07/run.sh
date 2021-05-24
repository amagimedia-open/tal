#!/bin/bash

set -u

function fnxOnEnd
{
    rm $TMP1 $TMP2
    trap '' 0 1 2 3 6 9 11
}

TMP1=`mktemp`
TMP2=`mktemp`

DIRNAME=$(readlink -e $(dirname $0))

source $TAL_VENV_ACTIVATE_FILE_PATH

python $DIRNAME/run.py run.py 2>/dev/null |\
python $DIRNAME/csvfy_ci_records.py > $DIRNAME/tx_recs.csv

cat $DIRNAME/tx_recs.csv |\
python $DIRNAME/tx_tree.py > $DIRNAME/tx_tree.txt

cat $DIRNAME/tx_recs.csv |\
python $DIRNAME/ci_seq_diag.py > $DIRNAME/tx_seq_diag.txt

java -jar $TAL_FOLDER_PATH/3rdparty/plantuml.jar $DIRNAME/tx_seq_diag.txt

set +u
deactivate


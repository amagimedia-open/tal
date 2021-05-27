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

cat <<EOD > $TMP1
COMPONENT,URL
ss,file://$DIRNAME/data/ss.html
sr,file://$DIRNAME/data/sr.html
sis,file://$DIRNAME/data/sis.html
plyr,file://$DIRNAME/data/plyr.html
EOD

source $TAL_VENV_ACTIVATE_FILE_PATH

cd $DIRNAME

rm -vrf output

mkdir output

export TAL_TX_NODE_TEMPLATE_FILEPATH=$PWD/data/tx_node_template.dot

#---[transform ci records to csv format]---

python run.py run.py 2>/dev/null |\
python csvfy_ci_records.py > output/tx_recs.csv

#---[create a text tree visualization]---

cat output/tx_recs.csv | python tx_tree.py > output/tx_tree.txt

#---[create a graphviz tree visualization]---

cat output/tx_recs.csv | python tx_dot_tree.py > output/tx_tree.dot
dot -Tpng output/tx_tree.dot -o output/tx_tree.png

#---[create a graphviz tree visualization with hrefs]---

cat output/tx_recs.csv |\
    python tx_href_dot_tree.py $TMP1 \
    > output/tx_href_tree.dot
dot -Tsvg output/tx_href_tree.dot -o output/tx_href_tree.svg

#---[create a uml sequence diagram visualization with hrefs]---

cat output/tx_recs.csv |\
    python ci_seq_diag.py $TMP1 \
    > output/tx_seq_diag.txt
java -jar $TAL_FOLDER_PATH/3rdparty/plantuml.jar -tsvg output/tx_seq_diag.txt

set +u
deactivate


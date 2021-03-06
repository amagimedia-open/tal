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
rm -rf output
mkdir output
cp $PWD/data/tx_seq_diag_*.html output
export TAL_TX_NODE_TEMPLATE_FILEPATH=$PWD/data/tx_node_template.dot

#---[transform ci records to csv format]---

echo "ci records --> csv format" >&2

python run.py

python run.py 2>/dev/null |\
python csvfy_ci_records.py > output/tx_recs.csv

csvlook output/tx_recs.csv > output/01_tx_recs.csv.txt

#---[create a text tree visualization]---

echo "csv format --> text tree" >&2

cat output/tx_recs.csv | python tx_tree.py > output/02_tx_tree.txt

#---[create a graphviz tree visualization]---

echo "csv format --> graphviz tree" >&2

cat output/tx_recs.csv | python tx_dot_tree.py > output/03_tx_tree.dot
dot -Tpng output/03_tx_tree.dot -o output/03_tx_tree.png

#---[create a graphviz tree visualization with hrefs]---

echo "csv format --> graphviz tree with hrefs" >&2

cat output/tx_recs.csv |\
    python tx_href_dot_tree.py $TMP1 \
    > output/04_tx_href_tree.dot
dot -Tsvg output/04_tx_href_tree.dot -o output/04_tx_href_tree.svg

#---[create a uml sequence diagram visualization with hrefs]---

echo "csv format --> uml sequence diagram with hrefs" >&2

cat output/tx_recs.csv |\
    python ci_seq_diag.py $TMP1 \
    > output/05_tx_seq_diag.txt
java -jar $TAL_FOLDER_PATH/3rdparty/plantuml.jar -tsvg output/05_tx_seq_diag.txt
sed -i -e '1,$ s/target="_top"/target="content"/g' output/05_tx_seq_diag.svg

set +u
deactivate


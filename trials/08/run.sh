#!/bin/bash

#see https://plantuml.com/starting

set -u
set -x

DIRNAME=$(readlink -e $(dirname $0))

java -jar $TAL_FOLDER_PATH/3rdparty/plantuml.jar sequenceDiagram.txt


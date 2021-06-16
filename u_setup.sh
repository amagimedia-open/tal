#!/bin/bash

set -u
#set -x

#TODO: need to write a makefile for this

#+---------+
#| GLOBALS |
#+---------+

DIRNAME=$(readlink -e $(dirname $0))
MODNAME=$(basename $0)

#+-------------------+
#| COMMAND LINE OPTS |
#+-------------------+

OPT_CLEAN=0
OPT_ALL=0
OPT_VENV=0
OPT_JAVA=0
OPT_SIMPY=0
OPT_GRPC=0
OPT_HASHIDS=0

if [[ $# -gt 0 ]]
then
    ARGS="$*"

    if [[ $ARGS =~ -h ]]
    then
        echo "usage: $MODNAME [-h] [clean|venv|simpy|grpc|hashids|java|all]" >&2
        exit 0
    fi

    [[ $ARGS =~ clean ]]   && { OPT_CLEAN=1; }
    [[ $ARGS =~ venv  ]]   && { OPT_VENV=1; }
    [[ $ARGS =~ simpy ]]   && { OPT_SIMPY=1; }
    [[ $ARGS =~ grpc  ]]   && { OPT_GRPC=1; }
    [[ $ARGS =~ hashids ]] && { OPT_HASHIDS=1; }
    [[ $ARGS =~ java  ]]   && { OPT_JAVA=1; }
    [[ $ARGS =~ all   ]]   && { OPT_ALL=1; }
fi

#+-----------------------------+
#| source enviroment variables |
#+-----------------------------+

source $DIRNAME/set_env_vars.sh

#+-----------+
#| functions |
#+-----------+

function safe_rmdir
{
    local _folder="$1"

    if [[ -d $_folder ]]
    then
        (
            if cd $_folder
            then
                echo "$MODNAME:removing contents of folder $_folder ..." >&2
                rm -rf ./*
                rm -f .*
            fi
        )

        echo "$MODNAME:removing folder $_folder ..." >&2
        rmdir $_folder
    fi
}

#+---------+
#| cleanup |
#+---------+

if ((OPT_CLEAN))
then
    safe_rmdir $TAL_VENV_FOLDER_PATH
    exit 0
fi

#+----------------------------+
#| install python virtual env |
#+----------------------------+

if ! dpkg -L python3-venv > /dev/null 2>&1
then
    sudo apt-get install python3-venv
fi

#+----------------------------+
#| create virtual environment |
#+----------------------------+

if ((OPT_ALL || OPT_VENV))
then
    safe_rmdir $TAL_VENV_FOLDER_PATH

    if ! mkdir -p $TAL_VENV_FOLDER_PATH
    then
        echo "$MODNAME:could not create folder $TAL_VENV_FOLDER_PATH" >&2
        exit 1
    fi

    (
        echo "$MODNAME:creating python virtual environment at folder $TAL_VENV_FOLDER_PATH ..." >&2
        cd $TAL_VENV_FOLDER_PATH
        python3 -m venv env
    )
fi

#+---------------+
#| install stuff |
#+---------------+

if [[ ! -f $TAL_VENV_ACTIVATE_FILE_PATH ]]
then
    echo "$MODNAME:virtual environment not created. use -h option for help" >&2
    exit 1
fi

if ((OPT_ALL || OPT_JAVA))
then
    sudo apt update

    java -version
    RET=$?
    if ((RET == 127))
    then
        sudo apt install default-jre
    fi

    javac -version
    RET=$?
    if ((RET == 127))
    then
        sudo apt install default-jdk
    fi
fi

source $TAL_VENV_ACTIVATE_FILE_PATH

    #+-------------+
    #| upgrade pip |
    #+-------------+

    python -m pip install --upgrade pip

    #+---------------+
    #| install simpy |
    #+---------------+

    if ((OPT_ALL || OPT_SIMPY))
    then
        pip install -U simpy
        #pip install -U pytest
    fi

    if ((OPT_ALL || OPT_GRPC))
    then
        #https://grpc.io/docs/languages/python/quickstart/
        python -m pip install grpcio
        python -m pip install grpcio-tools
        git clone -b v1.38.0 https://github.com/grpc/grpc
    fi

    if ((OPT_ALL || OPT_HASHIDS))
    then
        pip install hashids
    fi

set +u
deactivate


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

#+----------------------+
#| activate python venv |
#+----------------------+

source $TAL_VENV_ACTIVATE_FILE_PATH
cd $DIRNAME

#+---------------+
#| generate stub |
#+---------------+

rm -vf helloworld_pb2.py helloworld_pb2_grpc.py

python \
    -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    helloworld.proto

echo "generated rpc stub"

#+--------------+
#| start server |
#+--------------+

python greeter_server.py &
SERVER_PID=$!
disown #https://stackoverflow.com/a/23645819/1029379
echo "started server at pid $SERVER_PID"
sleep 2

#+--------------+
#| start client |
#+--------------+

python greeter_client.py

#+-------------+
#| stop server |
#+-------------+

sleep 2
echo "stopping server at pid $SERVER_PID"
kill $SERVER_PID 
sleep 1
if ps -p $SERVER_PID 2>/dev/null
then
    kill -9 $SERVER_PID
fi

#+------------------------+
#| deactivate python venv |
#+------------------------+

set +u
deactivate


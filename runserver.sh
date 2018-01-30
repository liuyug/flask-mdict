#!/bin/bash

export FLASK_APP=server.app
export PYTHONPATH=$PYTHONPATH;`pwd`

if [ "x$1" = "xrelease" ];then
    export FLASK_DEBUG=0
    export APP_CONFIG_FILE="`pwd`/config/release.py"
else
    export FLASK_DEBUG=1
    export APP_CONFIG_FILE="`pwd`/config/debug.py"
fi

echo $APP_CONFIG_FILE
flask run

# vim: tabstop=4 shiftwidth=4 expandtab

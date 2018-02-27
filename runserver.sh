#!/bin/bash

export FLASK_APP=server.app
export PYTHONPATH="`pwd`:$PYTHONPATH"

if [ "x$1" = "xrelease" ];then
    export FLASK_DEBUG=0
    export APP_CONFIG_FILE="../config/release.py"
else
    export FLASK_DEBUG=1
    export APP_CONFIG_FILE="../config/debug.py"
fi

echo "python path: $PYTHONPATH"
echo "config     : $APP_CONFIG_FILE"
flask run

# vim: tabstop=4 shiftwidth=4 expandtab

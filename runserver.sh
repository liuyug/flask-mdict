#!/bin/bash

export FLASK_APP=server.app
export PYTHONPATH="`pwd`:$PYTHONPATH"

if [ "x$1" = "xrelease" ];then
    export APP_CONFIG_FILE="../config/release.py"
else
    export FLASK_ENV=development
    export APP_CONFIG_FILE="../config/debug.py"
fi

echo "python path: $PYTHONPATH"
echo "config     : $APP_CONFIG_FILE"
flask run

# vim: tabstop=4 shiftwidth=4 expandtab

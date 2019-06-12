#!/bin/bash

if [ "x$1" = "x" ]; then
    today=`date +%Y%m%d`
else
    today=$1
fi
echo "run it after $today 18:00"

# import daily quote
python3 stock_kline.py tdx --import-day-cod --cod-date $today

# create tpo
python3 web_admin.py --send-tpo --tpo-source db --output-dir build

# check ma
python3 stock_analyst.py --ma -

# vim: tabstop=4 shiftwidth=4 expandtab

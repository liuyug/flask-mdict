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
python3 web_admin.py --send-tpo --tpo-source db --output-dir ~/Desktop/temp

ma="database/ma_$today.txt"
# check ma
python3 stock_analyst.py --ma --before-year 2 --source db --output $ma -

count=`cat $ma | wc -l`
echo "$today,$count" >> "database/ma_stat.csv"
tail "database/ma_stat.csv"



# vim: tabstop=4 shiftwidth=4 expandtab

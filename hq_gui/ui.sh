#!/bin/bash

set -e

uic='pyuic5'

ui_dir='gui/ui'

for ui_file in `ls $ui_dir/*.ui`; do
    b=`basename $ui_file .ui`
    echo "Find \"$ui_file\", generate \"ui_$b.py\""
    $uic -o "$ui_dir/ui_$b.py" $ui_file
done

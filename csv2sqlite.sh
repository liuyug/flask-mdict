#!/bin/sh

if [ x"$1" = "x" ]; then
    echo "usage: $0 <csv file>"
    exit 1
fi

csv_file=$1
db_name=`basename $csv_file .csv`

sqlite3 "${db_name}.db" <<EOD

DROP TABLE IF EXISTS $db_name;

.mode csv
.import $csv_file $db_name

CREATE INDEX ${db_name}_index_word ON $db_name(word);

.schema
EOD

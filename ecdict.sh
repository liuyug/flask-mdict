#!/bin/sh

ecdict_csv='https://github.com/skywind3000/ECDICT/raw/master/ecdict.csv'

if [ x"$1" = "x" ]; then
    echo "usage: $0 <csv file>"
    echo ""
    echo "1. download ecdict"
    echo "wget $ecdict_csv"
    echo "2. convert ecdict.csv to ecdict.db"
    echo "$0 ecdict.csv"
    exit 1
fi

csv_file=$1
db_name=`basename $csv_file .csv`

sqlite3 "${db_name}.db" <<EOD

DROP TABLE IF EXISTS $db_name;

.mode csv
.import $csv_file $db_name

DROP INDEX IF EXISTS ${db_name}_index_word;
CREATE INDEX ${db_name}_index_word ON $db_name(word);

.schema
EOD

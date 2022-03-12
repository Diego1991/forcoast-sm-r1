#!/bin/bash
# docker run forcoast-sm-r1 southern_north_sea "2021-11-29" 8 2.5 52

INITIAL_DIR="$(pwd)"

cd /usr/src/app

pip install --user -r required.txt

if [[ "$1" == "galway" ]]; then 
pilot_id=5
elif [ "$1" == "bay_of_biscay" ]; then 
pilot_id=2
elif [ "$1" == "southern_north_sea" ]; then 
pilot_id=4
elif [ "$1" == "limfjord" ]; then 
pilot_id=6
elif [ "$1" == "northern_adriatic_sea_pilot" ]; then 
pilot_id=8 
fi

echo "python SM-R1.py -t "$2T00:00:00" -x $4 -y $5 -p $pilot_id -d $3"
python SM-R1.py -t "$2T00:00:00" -x $4 -y $5 -p $pilot_id -d $3

echo "python bulletin_script.py -t "$2T00:00:00" -x $4 -y $5 -p $pilot_id -d $3"
python bulletin_script.py -x $4 -y $5 -p $pilot_id -d $3

python send_bulletin.py -T $6 -C $7 -B /usr/src/app/OUTPUT/BULLETIN/bulletin.png -M file

cp /usr/src/app/OUTPUT/BULLETIN/bulletin.png $INITIAL_DIR

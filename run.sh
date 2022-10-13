#!/bin/bash

#(C) Copyright FORCOAST H2020 project under Grant No. 870465. All rights reserved.

# Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2022 Marine Institute, Deltares
#       Diego Pereiro, Gido Stoop
#
#       diego.pereiro@marine.ie, gido.stoop@deltares.nl
#
#   This library is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this library.  If not, see <http://www.gnu.org/licenses/>.
#   --------------------------------------------------------------------

# docker run forcoast-sm-r1 southern_north_sea "2021-11-29" 8 2.5 52

INITIAL_DIR="$(pwd)"

cd /usr/src/app

#pip install --user -r required.txt

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

echo "python SM-R1.py -t $2 -x $4 -y $5 -p $pilot_id -d $3"
python SM-R1.py -t $2 -x $4 -y $5 -p $pilot_id -d $3

echo "python bulletin_script.py -t $2 -x $4 -y $5 -p $pilot_id -d $3"
python bulletin_script.py -x $4 -y $5 -p $pilot_id -d $3

python send_bulletin.py -T $6 -C $7 -B /usr/src/app/OUTPUT/BULLETIN/bulletin.mp4 -M video
#convert /usr/src/app/OUTPUT/HEAT/H.gif -layers Coalesce -resize 1020x659 -layers Optimize /usr/src/app/OUTPUT/HEAT/H_resize.gif
#convert /usr/src/app/OUTPUT/FLOATS/F.gif -layers Coalesce -resize 1020x659 -layers Optimize /usr/src/app/OUTPUT/FLOATS/F_resize.gif

#python send_bulletin.py -T $6 -C $7 -B /usr/src/app/OUTPUT/HEAT/H_resize.gif -M document
#python send_bulletin.py -T $6 -C $7 -B /usr/src/app/OUTPUT/FLOATS/F_resize.gif -M document

cp /usr/src/app/OUTPUT/BULLETIN/bulletin.mp4 $INITIAL_DIR
cp /usr/src/app/OUTPUT/BULLETIN/bulletin.webm $INITIAL_DIR

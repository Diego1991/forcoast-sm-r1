#!/bin/bash

Help()
{
echo "Usage: forcoast-sm-r1 [OPTIONS]"
echo ""
echo "Run FORCOAST R1 Service Module: Retrieve Sources of Contaminants"
echo ""
echo "OPTIONS:"
echo ""
echo "-h    Display help"
echo ""
echo "-p    Pilot number"
echo ""
echo "-s    Seeding method: either 'area' or 'point'"
echo ""
echo "-f    Farming areas file, used only if 'area' seeding has been selected"
echo ""
echo "-x    Seeding longitude, used only if 'point' seeding has been selected"
echo ""
echo "-y    Seeding latitude, used only if 'point' seeding has been selected"
echo ""
echo "-r    Uncertainty radius, used only if 'point' seeding has been selected"
echo ""
echo "-l    Seeding level: either 'surface' or 'bottom'"
echo ""
echo "-t    Seeding time with format 'yyyy-mm-dd HH:MM:SS'"
echo ""
echo "-u    Time uncertainty [h] before and after the selected time"
echo ""
echo "-d    Tracking time span [h]"
echo ""
echo "-m    Tracking mode: either -1 (backward) or +1 (forward)"
}

ARGS=""
BULL=""

while getopts ":hd:f:l:m:p:r:s:t:u:x:y:" option; do
     case $option in
          h)
             Help
	     exit;;

          p)
             ARGS="$ARGS -p $OPTARG"
             BULL="$BULL -p $OPTARG";;

          s)
             ARGS="$ARGS -s $OPTARG";;

          f)
             ARGS="$ARGS -f $OPTARG";;

          x)
             ARGS="$ARGS -x $OPTARG"
             BULL="$BULL -x $OPTARG";;

          y)
             ARGS="$ARGS -y $OPTARG"
             BULL="$BULL -y $OPTARG";;

          r)
             ARGS="$ARGS -r $OPTARG";;

          l)
             ARGS="$ARGS -l $OPTARG";;

          t)
             ARGS="$ARGS -t $OPTARG";;

          u)
             ARGS="$ARGS -u $OPTARG";;

          d)
             ARGS="$ARGS -d $OPTARG"
             BULL="$BULL -d $OPTARG";;

          m) 
             ARGS="$ARGS -m $OPTARG";;
             
         \?)
             echo "Error: invalid option"
             exit;;

     esac
done


INITIAL_DIR="$(pwd)"

#cd /usr/src/app

#pip install --user -r required.txt

echo "python SM-R1.py $ARGS"
echo "python bulletin_script.py $BULL"

#cp /usr/src/app/OUTPUT/BULLETIN/bulletin.png $INITIAL_DIR

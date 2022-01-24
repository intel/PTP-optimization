#!/bin/bash
# Copyright (c) 2021 Intel
# Licensed under the GNU General Public License v2.0 or later (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     https://spdx.org/licenses/GPL-2.0-or-later.html

#parse the commandline
while [[ "$#" -gt 0 ]]
do
    case $1 in
        -t|--timeout) TIMEOUT="$2"; shift ;;
        -s) S_VAL="$2"; shift ;;
	-c) C_VAL="$2"; shift ;;
	-P) P_VAL="$2"; shift ;;
	-I) I_VAL="$2"; shift ;;
	-v|--verbose) VERBOSE=1 ;;
#	-o|--offset) OFFSET=$2; shift;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

#check if S has a valid PTP clock assigned
if [ ! $S_VAL = "CLOCK_REALTIME" ]
then
	if [ ! -d "/sys/class/net/$S_VAL" ]
	then
		echo "Adapter $S_VAL does not exist."
		exit 1
	fi

	if [ ! -d "/sys/class/net/$S_VAL/device/ptp" ]
	then
		echo "Adapter does not have any PTP clocks"
		exit 1
	fi

#	optionally, set the start time od the PTP device under test, i.e.: testptp -d $PTP_DEV -s
#	PTP_DEV="/dev/"$(ls -1 /sys/class/net/$S_VAL/device/ptp)
#	[ ! -z $OFFSET ] && testptp -d $PTP_DEV -t $OFFSET
fi

#check if C has a valid PTP clock assigned
if [ ! $C_VAL = "CLOCK_REALTIME" ]
then
        if [ ! -d "/sys/class/net/$C_VAL" ]
        then
                echo "Adapter $C_VAL does not exist."
                exit 1
        fi

        if [ ! -d "/sys/class/net/$C_VAL/device/ptp" ]
        then
                echo "Adapter does not have any PTP clocks"
                exit 1
        fi

        C_VAL="/dev/"$(ls -1 /sys/class/net/$C_VAL/device/ptp)
#	optionally, add code for clearing current frequency corrections
#	./clearadj/clearadj
fi

#Build the command
CMD="phc2sys -s $S_VAL -m -c $C_VAL -O 0 -N 20"
DIR="phc2sys"
[ -n $P_VAL ] && CMD=$CMD" -P $P_VAL" DIR=$DIR"_P$P_VAL"
[ -n $I_VAL ] && CMD=$CMD" -I $I_VAL" DIR=$DIR"_I$I_VAL"
[ -n $TIMEOUT ] && CMD="timeout $TIMEOUT $CMD"
CMD="$CMD > $DIR.log"

if [[ -n "$VERBOSE" ]]
then
	echo "CMD: $CMD"
	echo "TIMEOUT: $TIMEOUT"
	echo "S_VAL: $S_VAL"
        echo "C_VAL: $C_VAL"
        echo "P_VAL: $P_VAL"
        echo "I_VAL: $I_VAL"
	echo "verbose $VERBOSE"
fi

eval $CMD
chmod 600 "$DIR.log"

[[ ! -d "$DIR" && ! -L "$DIR" && ! -f "$DIR" ]] && mkdir $DIR
python3 parse_ptp.py --input $DIR.log --plot
mv $DIR.log $DIR
mv test.png $DIR/$DIR.png
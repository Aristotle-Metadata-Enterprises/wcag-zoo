#!/usr/bin/env bash
npm install temp
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
pip install -e .

for SCRIPT in ./docs/development/scripts/*
do
    echo -n $SCRIPT " ... "
	if [ -f $SCRIPT -a -x $SCRIPT ]
	then
		OUT=`$SCRIPT`
        if [[ $OUT == *"1 failures"* ]]
        then
            echo good
        else
            echo bad
    		echo $OUT
        fi
	fi
done

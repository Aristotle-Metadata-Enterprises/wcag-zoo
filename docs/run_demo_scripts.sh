#!/usr/bin/env bash

# install requirements for scripts
npm install temp

# Python 3 stuff
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

let errored_builds=0
for SCRIPT in ./docs/development/scripts/*
do
	if [ -f $SCRIPT -a -x $SCRIPT ]
	then
        echo -n $SCRIPT " ... "
		OUT=`$SCRIPT`
        if [[ $OUT == *"1 failures"* ]]
        then
            echo "good"
        else
            let errored_builds=$((errored_builds+1))
            echo "bad"
    		echo $OUT
        fi
	fi
done

exit $errored_builds

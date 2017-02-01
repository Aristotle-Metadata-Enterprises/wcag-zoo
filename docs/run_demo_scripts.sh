#!/usr/bin/env bash

# install requirements for scripts
npm install temp
cpan-install JSON

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

let errored_builds=0
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
            let errored_builds=$((errored_builds+1))
            echo bad
    		echo $OUT
        fi
	fi
done
echo $errored_builds
exit $errored_builds

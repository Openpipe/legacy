#!/bin/sh
set -eu

pluginList=$(find mdatapipe/plugins/ -name "*.py" | grep -v "__init__" | sort)
for pluginFile in $pluginList
do
	testFile=$(echo tests$pluginFile | sed "s/\.py/.yaml/g" | sed "s/mdatapipe//g")
	if [ ! -r $testFile ]; then
		mkdir -p $(dirname $testFile)
		echo $testFile is missing !!!
		exit 1
	fi
done

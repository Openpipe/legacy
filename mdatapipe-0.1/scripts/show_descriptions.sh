#!/bin/sh
set -eu
IFS=$'\n'
desc_list=
for line in $(find mdatapipe/plugins/ -name "*.py"| xargs -n1 egrep -H "^Description" | sed "s#mdatapipe/plugins/##g" | sort )
do
    plugin_name=$(echo $line |cut -d: -f1| sed "s#/# #g"| sed "s/.py//g")
    plugin_desc=$(echo $line |cut -d: -f3-)
    echo $plugin_name:$plugin_desc
done

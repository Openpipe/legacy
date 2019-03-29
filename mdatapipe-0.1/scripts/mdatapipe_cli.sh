#!/bin/sh
SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
"$SCRIPTPATH"/../bin/python -m mdatapipe.client $*

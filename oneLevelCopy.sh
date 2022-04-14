#!/usr/bin/env bash

from=$1
to=$2
ext="*"

if test "$#" -le 1; then
    echo "Illegal number of parameters"
    echo "usage:"
    echo "    oneLevelCopy.sh <source directory> <outDirectoru> [extension]"
    echo "Lo scopo dello script è copiare tutti i file conenuti nelle sotto directory ad un unico livello"
    exit
fi

if test "$#" -ge 3; then
    ext=$3
fi

echo "Script will copy all sub file from '$from', to '$to', with extension $ext"

find "$from" -type f -name "*.$ext" -exec cp {} "$to" \;
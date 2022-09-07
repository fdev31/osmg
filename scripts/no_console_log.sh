#!/bin/sh
for fname in $* ; do
    if grep console.log $fname ; then
        exit 1
    fi
done

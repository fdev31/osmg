#!/bin/sh
for fname in $* ; do
    if grep console.log $fname ; then
        echo "ERROR: Remove usage of \"console.log\" in $fname and re-try."
        exit 1
    fi
done

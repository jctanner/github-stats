#!/bin/bash

# -s, --nocapture

#ARGS="-w test/unit"
#/opt/anaconda2/bin/nosetests $ARG $@

cd test/unit
/opt/anaconda2/bin/nosetests $@

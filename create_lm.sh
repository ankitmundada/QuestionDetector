#!/bin/bash

# Usage: create_lm.sh TEXT_FILE ARPA_FILE BIN_FILE

if [[ $# -lt 3 ]]; then
    echo "Give all Params"
    exit 1
fi

# building arpa file
kenlm/build/bin/lmplz -o 5 < $1 > $2

# building binary file
kenlm/build/bin/build_binary -s $2 $3

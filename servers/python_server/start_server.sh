#!/bin/bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

cd "$parent_path"

export PYTHONPATH="$parent_path"/gen_py:$PYTHONPATH
export PYTHONPATH="$parent_path":$PYTHONPATH

echo "$PYTHONPATH"

# uses system python interpreter
python3 "$parent_path"/myserver/pythonserver.py &

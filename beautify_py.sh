#!/bin/bash

set -e
set -x

python="python"

$python -V
$python -m pip install -U pip
$python -m pip install -U flake8 ruff pyupgrade

REQ_FILES=`find . -name "requirements.txt"`
for REQ_FILE in $REQ_FILES; do
    $python -m pip install -r $REQ_FILE
done
find . -name "*.py" | xargs dos2unix
find . -name "*.py" | xargs $python -m isort
find . -name "*.py" | xargs $python -m black -l 120
find . -name "*.py" | xargs $python -m flake8 --extend-ignore=E203,E402,F403,F401 --max-line-length 999
find . -name "*.py" | xargs $python -m pyupgrade --py311-plus
find . -name "*.py" | xargs $python -m pylint --disable=line-too-long,broad-except,W,C,duplicate-code
$python -m ruff .

echo "Done for all"

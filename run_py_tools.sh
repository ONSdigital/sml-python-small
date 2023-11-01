#!/bin/sh

CMDS=("black --check --diff freeze.py sml_small features" "pylint freeze.py sml_builder features" "flake8 freeze.py sml_builder features" "isort --check-only ." "bandit -c pyproject.toml -r .")

for i in "${CMDS[@]}"
do 
    if $i
    then
        echo "$i command successfully executed"
    else
        echo "$i command failed to execute or display errors that needs to be corrected"
    fi
done
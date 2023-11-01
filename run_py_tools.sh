#!/bin/sh

CMDS=("black --check --diff sml_small tests" "pylint sml_small tests" "flake8 sml_small tests" "isort --check-only ." "bandit -c pyproject.toml -r .")

for i in "${CMDS[@]}"
do 
    if $i
    then
        echo "$i command successfully executed"
    else
        echo "$i command failed to execute or display errors that needs to be corrected"
    fi
done
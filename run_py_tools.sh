#!/bin/sh

CMDS=("black --check --diff sml_small tests" "flake8 sml_small tests" "isort --check-only ." "bandit -c pyproject.toml -r .")

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'  # No color
results=()
for i in "${CMDS[@]}"
do 
    if $i
    then
        results+=("$(printf "%-40s" "$i"): ${GREEN}Success${NC}")
        echo "$i command successfully executed"
    else
        results+=("$(printf "%-40s" "$i"): ${RED}Failure${NC}")
        echo "$i command failed to execute or displays errors that needs to be corrected"
    fi
done

cd tests
pytest
cd ..

echo "Test Results:"
for result in "${results[@]}"
do
    echo "$result"
done
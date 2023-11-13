#!/bin/sh

CMDS=("black --diff sml_small tests" "flake8 sml_small tests" "isort ." "bandit -c pyproject.toml -r .")
 
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'  # No color
results=()
return_val=0
for i in "${CMDS[@]}"
do 
    if $i
    then
        results+=("$(printf "%-40s" "$i"): ${GREEN}Success${NC}")
        echo "$i command successfully executed"
    else
        return_val=1
        results+=("$(printf "%-40s" "$i"): ${RED}Failure${NC}")
        echo "$i command failed to execute or displays errors that needs to be corrected"
    fi
done

cd tests
pytest
return_val=$((return_val || $?)) 
cd ..

echo "Test Results:"
for result in "${results[@]}"
do
    echo "$result"
done

exit "$return_val"

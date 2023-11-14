# SML-PYTHON-SMALL

##### Statistical Methods Library for Python Pandas methods used in the **S**tatistical **P**roduction **P**latform (SPP).

This library contains pandas statistical methods that are only suitable for use on small datasets which can safely be processed in-memory.

For further information about the methods contained in this module see the [method specifications](https://github.com/ONSdigital/Statistical-Method-Specifications)

For user documentation and example data relating to the methods in this module see the [supporting information](https://github.com/ONSdigital/sml-supporting-info)

### Automated testing
In order to ensure code quality, there is a manual test script provided __run_py_tools.sh__ which will run linting, code formatting checks, and the pytest suite. 

It is often easy to forget to check code formatting before pushing to the remote repository, so there is the option of running the testing script automatically by using the git hook __pre-push__. This means that when __git push__ is run, the test script will be run first, and will abort the push if any of the tests fail.

Git hooks cannot be pushed to the remote repository so if you would like this script to be run automatically you will need to follow these steps:

 - Check that the __.git__ directory is present in your repository by running __ls -a__ in the terminal
 - Run __cd .git/hooks__ and open the file marked __pre-push.sample__ in a code editor
 - Replace the content of this file with the following code:
 ```bash
#!/bin/sh
GREEN='\033[1;32m'
RED='\033[1;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

git stash clear # in case there is nothing to stash,
# then the stash needs to be empty, else previously 
# stashed changes will be incorrectly restored

git stash
testing_script="./run_py_tools.sh"


if "$testing_script"; then
    echo "${GREEN}./run_py_tools script passes, proceeding with push...${NC}"
    git add . # commit any changes made by the pytools script
    git commit -m "run_py_tools auto-formatting"
    git stash apply
    echo "${YELLOW}NOTE: If any commits were made by the auto-formatting tool, then they will not be automatically pushed. You will need to run git push again (or git push --no-verify if you don't want to run the test suite again).${NC}"
    exit 0
else
    echo "${RED}./run_py_tools script fails, push aborted.${NC}"
    git checkout . # revert any changes made by the pytools script
    git stash apply
    exit 1
fi

```
- Save the file and __rename it to pre-push__ (i.e. remove the .sample suffix from the filename)
- Run __cd ../..__ to change the current working directory back to the root directory of the sml-python-small repository
- Open a poetry shell and run __git push__ to check if the testing tools work (it doesn't matter if there is nothing to push, the pre-push hook will still run).
- After all of the tests have run, you should see something like this:
```bash
================================================================================= 443 passed in 12.58s ==================================================================================
Test Results:
black --check --diff sml_small tests    : Success
flake8 sml_small tests                  : Success
isort --check-only .                    : Success
bandit -c pyproject.toml -r .           : Success
./run_py_tools script passes, proceeding with push...
Everything up-to-date
```
- If any of the linting tests or pytest files fail then the push will be aborted.

#### Troubleshooting
 - In order to push, you need to run the __git push__ command in a poetry shell, otherwise all of the tests will fail.
 - You also need to ensure that your current working directory in the terminal is within the sml-python-small repository.
 - While the script is running, any non-committed changes will be stashed. This means that any work after the commit has been made may seem to disappear for a moment during the tests. After the file has finished running, the stashed changes will be automatically restored. This is to ensure that the tests are being run on the code within the commits, rather than any non-committed changes.
 - If for any reason the script exits unexpectedly, you can restore the stashed changes manually by running the following command:
```bash
git stash apply
```
 - If any changes are made by the auto-formatting tool, then these will automatically be committed, but it is not possible to automatically push these changes. You can check by running __git log__. If the most recent commit is titled 'run_py_tools auto-formatting', then you will need to run __git push__ again (or __git push --no-verify__ if you don't want to run the test suite again).
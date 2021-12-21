#!/usr/bin/env bash
set -x

GIT_ROOT=$(git rev-parse --show-toplevel)
cd "$GIT_ROOT"

has_errors=0

# Code auto formatting check with black
poetry run black --skip-string-normalization --check .
GIT_STATUS="$(git status --porcelain)"
if [ "$GIT_STATUS" ];
then
  echo "Source code changes are not formatted with black (./dev/format.sh script)"
  echo "Files changed:"
  echo "------------------------------------------------------------------"
  echo "$GIT_STATUS"
  has_errors=1
else
  echo "Code auto formatting passed"
fi

# The first line of the tests are
# always empty if there are no linting errors

echo "Running flake8 on bentoctl module.."
output=$( poetry run flake8 --config=.flake8 bentoctl )
first_line=$(echo "${output}" | head -1)
echo "$output"
if [ -n "$first_line" ]; then
  has_errors=1
fi

echo "Running flake8 on test module.."
output=$( poetry run flake8 --config=.flake8 tests )
first_line=$(echo "${output}" | head -1)
echo "$output"
if [ -n "$first_line" ]; then
  has_errors=1
fi

echo "Running pylint on bentoctl module.."
output=$( poetry run pylint --rcfile="./pylintrc" bentoctl )
first_line=$(echo "${output}" | head -1)
echo "$output"
if [ -n "$first_line" ]; then
  has_errors=1
fi

echo "Running pylint on test module.."
output=$( poetry run pylint --rcfile="./pylintrc" tests )
first_line=$(echo "${output}" | head -1)
echo "$output"
if [ -n "$first_line" ]; then
  has_errors=1
fi

echo "Done"
exit $has_errors

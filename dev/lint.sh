#!/usr/bin/env bash

GIT_ROOT=$(git rev-parse --show-toplevel)
cd "$GIT_ROOT" || exit

echo "Running flake8 on bentoctl module.."
flake8 --config=.flake8 bentoctl

echo "Running flake8 on test module.."
flake8 --config=.flake8 tests

echo "Running pylint on bentoctl module.."
pylint --rcfile="./pylintrc" bentoctl

echo "Running pylint on test module.."
pylint --rcfile="./pylintrc" tests

echo "Done"

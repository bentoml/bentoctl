#!/usr/bin/env bash

# USAGE: release.sh <version> [<repo>]
# possible options for <repo>: testpypi or pypi
set -e

if [ "$#" -eq 1 ]; then
  VERSION_STR=$1
  REPO="testpypi"
  echo "Releasing version $VERSION_STR to $REPO"
elif [ "$#" -eq 2 ]; then
  VERSION_STR=$1
  REPO=$2
  echo "Releasing version $VERSION_STR to $REPO"
else
  echo "Usage: release.sh <version> [<repo>]"
  exit 1
fi

SEMVER_REGEX="^[vV]?(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)(\\-[0-9A-Za-z-]+(\\.[0-9A-Za-z-]+)*)?(\\+[0-9A-Za-z-]+(\\.[0-9A-Za-z-]+)*)?$"

if [[ "$VERSION_STR" =~ $SEMVER_REGEX ]]; then
  echo "Releasing bentoctl version v$VERSION_STR to $REPO"
else
  echo "Warning: version $VERSION_STR must follow semantic versioning schema, ignore this for preview releases"
fi

GIT_ROOT=$(git rev-parse --show-toplevel)
cd "$GIT_ROOT"

echo "Switching to main branch"
git checkout main


if [ -d "$GIT_ROOT"/dist ]; then
  echo "Removing existing 'dist' and 'build' directory to get a clean build"
  rm -rf "$GIT_ROOT"/dist
  rm -rf "$GIT_ROOT"/build
fi

tag_name="v$VERSION_STR"

echo "Update version in pyproject.toml..."
if [[ "$OSTYPE" =~ ^darwin ]]; then
  sed -i '' "s/^version = .*$/version = \"$VERSION_STR\"/" pyproject.toml
else
  sed -i "s/^version = .*$/version = \"$VERSION_STR\"/" pyproject.toml
fi

echo "Installing dev dependencies..."
poetry install

echo "Building pypi package..."
poetry build

if [ "$REPO" = "testpypi" ]; then
  echo "Publishing testpypi package..."
  poetry config repositories.testpypi https://test.pypi.org/legacy/
  poetry publish --repository $REPO
elif [ "$REPO" = "pypi" ]; then
  git add pyproject.toml
  git commit -m "Update version to $VERSION_STR"
  git push origin main

  if git rev-parse "$tag_name" >/dev/null 2>&1; then
    echo "git tag '$tag_name' exist, using existing tag."
    echo "To redo releasing and overwrite existing tag, delete tag with the following and re-run release.sh:"
    echo "git tag -d $tag_name && git push --delete origin $tag_name"
    git checkout "$tag_name"
  else
    echo "Creating git tag '$tag_name'"
    git tag -a "$tag_name" -m "Tag generated by bentoctl/dev/release.sh, version: $VERSION_STR"
    git push origin "$tag_name"
  fi

  echo "Publishing pypi package..."
  poetry publish
else
  echo "Unknown repo: $REPO"
  exit 1
fi

echo "published bentoctl version:$VERSION_STR to $REPO"

:; if [ -z 0 ]; then
  goto :WINDOWS
fi

set -x
poetry install
exit

:: cmd script
:WINDOWS
poetry install

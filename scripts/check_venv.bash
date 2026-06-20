#!/usr/bin/env bash

check_venv() {
  for d in $1
  do
    export d
    bash -c "
      echo Checking \$d;
      cd \$d;
      echo Current directory is \$(pwd);
      pipenv --venv;
      check_venv \"\$(find . -type d -path '*/*' -prune)\"
    "
  done
}

export -f check_venv

check_venv "$@" 2>&1

#!/usr/bin/env bash
# scripts/check_venv.bash
#
# Recursively verify pipenv venvs in the project tree.
#
# Author: notweerdmonk
# SPDX-License-Identifier: Apache-2.0
#
# Copyright 2026 notweerdmonk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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


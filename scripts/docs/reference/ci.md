# ci.sh

Full CI pipeline — builds + tests in one command.

## Overview

Build all packages via nox -s all_builds (creates dist/ wheels),
then run all test suites via nox -s all_tests. Builds first so that
dist/ directories exist when per-package tests resolve file://
dependency sources.



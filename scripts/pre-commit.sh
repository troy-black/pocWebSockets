#!/usr/bin/env bash

# Store current shell states
state="$(shopt -po xtrace noglob errexit)"

# Enable printing commands
set -x

ruff check ./../tdb --fix
ruff format ./../tdb
mypy ./../tdb

ruff check ./../migrations --fix
ruff format ./../migrations
mypy ./../migrations

#ruff check ./../tests --fix
#ruff format ./../tests
#mypy ./../tests

# restore to recorded state:
set +vx; eval "$state"

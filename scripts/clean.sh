#!/usr/bin/env bash

clear

# Store current shell states
state="$(shopt -po xtrace noglob errexit)"

# Enable printing commands
set -x

cd "$(dirname "$0")"

find ./../ -type d -name "__pycache__" -exec rm -rf {} +
find ./../ -type d -name ".mypy_cache" -exec rm -rf {} +
find ./../ -type d -name ".ruff_cache" -exec rm -rf {} +
find ./../ -type d -name ".uv_cache" -exec rm -rf {} +

source pre-commit.sh

# restore to recorded state:
set +vx; eval "$state"

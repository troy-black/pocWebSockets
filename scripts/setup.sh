#!/usr/bin/env bash

# Store current shell states
state="$(shopt -po xtrace noglob errexit)"

# Enable printing commands
set -x

cd "$(dirname "$0")"
cd ..
rm -rf .venv

if ! command -v uv 2>&1 >/dev/null
then
  echo "Downloading https://astral.sh/uv/install.sh"
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

uv python install '>=3.12,<3.13'
uv venv --python 3.12
source .venv/bin/activate
uv sync

# restore to recorded state:
set +vx; eval "$state"

#!/usr/bin/env bash
# Keep the original entry point; rendering and installation use Python's stdlib.
set -euo pipefail
KIT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
exec python3 "$KIT_DIR/scripts/install.py" "$@"

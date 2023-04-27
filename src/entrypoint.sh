#!/bin/sh

BIN_NAME="$(basename "$0")"
BIN_DIR="$(dirname "$0")"

/usr/bin/env SHIV_CONSOLE_SCRIPT="$BIN_NAME" "$BIN_DIR"/netrics "$@"

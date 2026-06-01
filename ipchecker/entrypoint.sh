#!/bin/sh
set -e

CACHE_FILE="/data/last_ip.json"

# 1. If nothing exists at the path, initialize a clean JSON file
if [ ! -e "$CACHE_FILE" ]; then
    echo "Entrypoint: No cache file found. Initializing clean JSON..."
    echo "{}" > "$CACHE_FILE"

# 2. If Docker accidentally mounted it as a directory, remove and correct it
elif [ -d "$CACHE_FILE" ]; then
    echo "Entrypoint: Found directory anomaly at $CACHE_FILE. Correcting..."
    rm -rf "$CACHE_FILE"
    echo "{}" > "$CACHE_FILE"
fi

# 3. Handoff system execution to the Python monitor process
exec python -u /app/ip_monitor.py

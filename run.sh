#!/bin/bash
echo "Starting Underground Bass bot"
while true; do
  uv run main.py 2>&1
  echo "Bot crashed. Restarting..."
done
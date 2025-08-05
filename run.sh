#!/bin/bash
echo "Starting Underground Bass bot"
while true; do
  uv run main.py
  echo "Bot crashed. Restarting in 2 seconds..."
  sleep 2
done
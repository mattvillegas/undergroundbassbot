#!/bin/bash
echo "Starting Underground Bass bot"
while true; do
  uv run main.py
  echo "Bot crashed. Restarting..."
done
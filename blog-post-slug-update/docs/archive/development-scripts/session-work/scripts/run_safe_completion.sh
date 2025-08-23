#!/bin/bash

# Safe batch completion script
# This script will complete the remaining URLs without touching existing results

echo "🔄 Starting Safe Batch Completion..."
echo "=================================="

# Activate virtual environment
source venv/bin/activate

# Prevent sleep during processing
caffeinate -d -i -m -s python3 safe_complete_batch.py

echo "✅ Safe completion finished!"
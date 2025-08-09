#!/bin/bash

echo "Cleaning up temporary files..."

# Remove temporary files
find . -name "*.pyc" -delete 2>/dev/null
find . -name "*.bin" -delete 2>/dev/null
find . -name "*_1.json" -delete 2>/dev/null
find . -name "*_debug.log" -delete 2>/dev/null
find . -name "*.log" -delete 2>/dev/null
find . -name "*.*~" -delete 2>/dev/null
find . -name "Thumbs.db" -delete 2>/dev/null

echo "Removing cache directories..."

# Remove cache directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name "CaptureFolder1" -exec rm -rf {} + 2>/dev/null
find . -type d -name "CaptureFolder2" -exec rm -rf {} + 2>/dev/null

echo "Cleanup complete!"
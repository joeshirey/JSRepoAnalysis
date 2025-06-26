#!/bin/bash

# Move errors.log to errors.copy.log, overwriting if it exists, and delete errors.log
mv errors.log errors.copy.log
rm errors.log

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting re-processing of files from errors.log..."

# Read errors.log line by line
while IFS=$'\t' read -r file_path error_message; do
    if [[ -n "$file_path" ]]; then
        echo "Processing: $file_path"
        # Call uv run main.py for each file path with --regen flag
        uv run main.py "$file_path" --regen
        echo "Finished processing: $file_path"
    fi
done < errors.copy.log

echo "Reprocessing complete."

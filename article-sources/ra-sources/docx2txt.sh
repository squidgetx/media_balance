#!/bin/bash

for file in "$1"/*.docx; do
    if [ -f "$file" ]; then
        output_file="${file%.*}.txt"
        pandoc "$file" -t plain > "$output_file"
        echo "Converted: $file"
    fi
done

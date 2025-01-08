#!/usr/bin/env bash

# Find files recursively, count lines, sort by line count (descending), and show top 10
find . -type f \
    -not -path "*/\.*" \
    -not -path "*/node_modules/*" \
    -not -path "*/build/*" \
    -not -path "*/dist/*" \
    -not -name "*.json" \
    -not -name "*.pdf" \
    -not -name "*.qcow2" \
    -not -name "*.zsh" \
    -not -name "*.css" \
    2>/dev/null | \
while read -r file; do
    if [ -f "$file" ]; then
        lines=$(wc -l < "$file" 2>/dev/null)
        if [ $? -eq 0 ]; then
            printf "%8d %s\n" "$lines" "$file"
        fi
    fi
done | \
sort -rn | \
head -n 10

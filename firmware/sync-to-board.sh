#!/bin/sh

echo "Creating directories ..."
for dir in $(find . -type d | cut -c 3-); do
    if [ "$dir" = '' ]; then
        continue
    fi
    echo "  $dir"
    ampy mkdir "$dir" 2>/dev/null
done

echo "Copying files ..."
for file in $(find . -name '*.py' | cut -c 3-); do
    echo "  $file"
    ampy put "$file" "$file"
done

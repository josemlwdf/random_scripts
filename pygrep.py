#!/bin/bash
# This Bash script executes a Python3 command to perform a text search within a file using Python's capabilities
# It resolves situations where 'grep' returns an error like 'grep: yourfile: binary file matches'
# Usage: pygrep [string] [file name]
# Example: pygrep 'search_string' 'file_to_search.txt'
python -c "with open('$2', 'r') as file: [print(line.strip()) for line in file if '$1' in line]"

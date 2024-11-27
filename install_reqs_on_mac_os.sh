#!/bin/bash
# shell script to identify the operating system of the user and install requirements for the project accordingly


# Detect the operating system
OS_TYPE=$(uname)

# Modify requirements.txt based on OS
if [[ "$OS_TYPE" == "Linux" || "$OS_TYPE" == "Darwin" ]]; then
    echo "Detected $OS_TYPE. Removing Windows-specific requirements (e.g., pywin32)..."

    # Create a new requirements file without Windows-specific dependencies
    grep -vE "pywin32|windows-specific-package" requirements.txt > temp_requirements.txt

    # Replace the old requirements file
    mv temp_requirements.txt requirements.txt

    echo "Updated requirements.txt for $OS_TYPE."
else
    echo "Running on Windows. No changes to requirements.txt."
fi

# Now run pip install
echo "Running pip install..."
pip install -r requirements.txt

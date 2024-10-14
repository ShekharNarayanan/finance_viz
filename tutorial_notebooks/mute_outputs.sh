'''
Delete any outputs from the jupyter notebooks that are associated with "print" or ".head()" statements.
'''
#!/bin/bash

# Check if there are any Jupyter notebooks in the current directory
notebooks=$(find . -name "*.ipynb")

if [ -z "$notebooks" ]; then
    echo "No Jupyter notebooks found in the current directory."
    exit 0
fi

# Process each notebook
for notebook in $notebooks; do
    echo "Clearing outputs in $notebook..."

    # Create a new filename with the _cleared suffix
    new_notebook="${notebook%.ipynb}.ipynb"

    # Run a Python script to clear outputs and save the new notebook
    python - <<END
import json

# Load the original notebook
with open('$notebook', 'r', encoding='utf-8') as f:
    notebook_data = json.load(f)

# Clear output cells in code cells
for cell in notebook_data.get('cells', []):
    if cell['cell_type'] == 'code':
        cell['outputs'] = []
        cell['execution_count'] = None  # Optionally clear execution count

# Save the modified notebook as a new file
with open('$new_notebook', 'w', encoding='utf-8') as f:
    json.dump(notebook_data, f, indent=2)

END

    echo "Cleared outputs and saved to $new_notebook."
done

echo "All outputs have been cleared and saved to new notebooks."
exit 0

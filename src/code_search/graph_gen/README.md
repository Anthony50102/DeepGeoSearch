# Instructions for Creating the JSONL File for Database Generation

To generate the necessary JSONL file for feeding into the database generation tool, follow these steps:

1. **Create the JSONL File:**
   - Use the `convert_repo_jsonl.py` script.
   - Pass the HTTPS URL of the desired open-source GitHub repository as an argument.
   - This will generate a JSONL file containing the functions from the repository.

2. **Generate Graph Representations:**
   - Execute the `build_python_graph.py` script.
   - This script will create graph representations for each function listed in the previously generated JSONL file.
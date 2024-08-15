import sys
import os
import json
import gzip
import argparse
import ast
import subprocess
from pathlib import Path
from tokenize import tokenize, TokenInfo
from io import BytesIO


def clone_repo(repo_url, clone_dir):
    """Clone the GitHub repository."""
    if os.path.exists(clone_dir):
        print(f"Directory {clone_dir} already exists.")
        subprocess.run(['rm', '-rf', clone_dir])
        # return
    subprocess.run(['git', 'clone', repo_url, clone_dir], check=True)


def extract_functions_from_file(filepath, file_content):
    """Extract functions and their details from a Python file."""
    tree = ast.parse(file_content, filename=filepath)
        
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_code = ast.get_source_segment(file_content, node)
            func_name = node.name
            for token in tokenize(BytesIO(func_code.encode('utf-8')).readline):
                print(token)
                break
            # sys.exit(0)
            code_tokens = [token.string for token in tokenize(BytesIO(func_code.encode('utf-8')).readline) if token.type == 1]  # Only names
            
            functions.append({
                'code': func_code,
                'code_tokens': code_tokens,
                'func_name': func_name,
                'language': 'python',
                'path': filepath,
                'repo': repo_name
            })
    
    return functions


def process_repo(clone_dir,save_path, delete=True):
    """Process the cloned repository and generate the JSONL file."""
    jsonl_file = f"python_{repo_name}_jsonl.gz"
    jsonl_file = os.path.join(save_path ,jsonl_file)
    with gzip.open(jsonl_file, 'wt', encoding='utf-8') as gz_file:
        for root, _, files in os.walk(clone_dir):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    functions = extract_functions_from_file(filepath, file_content)
                    for function in functions:
                        gz_file.write(json.dumps(function) + '\n')
    print(f"Data saved to {jsonl_file}")
    if delete:
        subprocess.run(['rm', '-rf', clone_dir])
        print(f"Deleted cloned GitHub repo")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Clone a GitHub repo and extract Python functions to a JSONL file.')
    parser.add_argument('repo_url', type=str, help='GitHub repository URL to clone.')
    parser.add_argument('save_path', type=str, help='Path to save output too')
    args = parser.parse_args()
    
    repo_name = args.repo_url.split('/')[-1].replace('.git', '')
    if not os.path.exists(args.save_path):
        print("Bad save path")
        sys.exit(0)
    clone_dir = os.path.join(os.getcwd(), repo_name)
    
    clone_repo(args.repo_url, clone_dir)
    process_repo(clone_dir, args.save_path)

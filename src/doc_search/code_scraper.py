import os
from tqdm import tqdm
import json
from doc_scraper import save_to_file_cheker
import argparse
import re

class CodeScraper:
    def __init__(self, url):
        self.https_url = url
        self.repo_name = ""
        self.functions = []

    def download_repo(self):
        # Get the repo name
        self.repo_name = ".".join(self.https_url.split("/")[-1].split(".")[0:2]) 

        # Send os command to clone the repository and wait until it is done
        try:
            os.popen(f"git clone {self.https_url}").read()
            return
        except Exception as e:
            print(f"Error cloning repository: {e}")
            return

    def read_functions(self):
        # Path to the cloned repository
        repo_path = os.path.join(os.getcwd(), self.repo_name)

        # Walk through the repository to read .cs files
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.cs'):
                    file_path = os.path.join(root, file)
                    self.extract_functions(file_path)

    def extract_functions(self, file_path):
        with open(file_path, 'r') as file:
            code = file.read()
        
        # Regular expression to match C# methods
        function_pattern = re.compile(
            r'((?:public|private|protected|internal|static|virtual|override|abstract|async|\s)+\s+\w+\s+\w+\s*\(.*?\)\s*{(?:[^{}]*{[^{}]*})*[^{}]*})', 
            re.DOTALL
        )
        
        # Find all functions in the code and append to the list as strings
        functions = function_pattern.findall(code)
        for func in functions:
            self.functions.append({"code": func, "file": file_path})

    def save_functions(self, output_file, override):
        # Save the functions to a file in json format
        print(output_file, override)
        if not override:
            output_file = save_to_file_cheker(output_file)

        with open(output_file, "w") as file:
            file.write(json.dumps(self.functions))
    

    def summarize_code_chunks(self, file_name = "summarized_code.json", openai = False):
        # Test a query
        # Instantiate the OpenAI class
        from openai import OpenAI
        client = OpenAI(
            organization='org-lWc2i4uug3zMNYepkbKKOBcC',
            project='proj_1NnIovGx9DVEXNBjN7gZo9vb',
            )
        
        for func in tqdm(self.functions, desc="Summarizing chunks", total=len(self.functions)):
            func["summary"] = client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Please convert this function to natural language keeping as much detail as possible: code: {func["code"]} file path: {func["file"]} A: "}
                ]
            ).choices[0].message.content
    
        # Save the summarized chunks
        self.save_functions(file_name, override=True)

    def crawl(self, output_file = "functions.json", override = False):
       self.download_repo()
       self.read_functions()
       self.summarize_code_chunks()

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--url", help="URL of the repository to scrape", required=True)
    argparser.add_argument("--output", help="Output file to save the functions") 
    argparser.add_argument("--override", help="Override the output file if it exists", action="store_true")
    args = argparser.parse_args()
    scraper = CodeScraper(args.url)
    scraper.crawl(override = args.override)
    for func in scraper.functions:
        print(func)

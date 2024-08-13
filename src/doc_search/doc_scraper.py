import os
from tqdm import tqdm
import argparse
import json
import sys
import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin, urlparse
from llama_parser import LlamaParser
from openai import OpenAI

def save_to_file_cheker(file_name):
    # Check if file already exists
    if os.path.exists(file_name):
        print(f"File {file_name} already exists. Do you want to overwrite it? (y/n)")
        response = input()
        if response.lower() == "y":
            print("Overwriting...")
            return file_name
        else:
            print("Would you like to save the file with a different name? (y/n)")
            response = input()
            if response.lower() == "y":
                print("Enter the new filename:")
                new_file_name = input()
                print("Overwiting...")
                return new_file_name
            else:
                print("Not saving the file and exiting...")
                sys.exit(0)
    else:
        return file_name

class Scaper:
    def __init__(self) -> None:
        self.visited_urls = set()
        self.list_of_text_chunks = []

    def is_valid_url(self, url, base_url):
        # Check if the URL is valid and belongs to the same domain
        parsed_base = urlparse(base_url)
        parsed_url = urlparse(url)
        return parsed_url.scheme in ('http', 'https') and parsed_base.netloc == parsed_url.netloc

    def crawl(self, url, base_url, max = None):
        if url in self.visited_urls:
            return
        if max is not None and len(self.visited_urls) >= max:
            return
        
        if max is not None:
            print(f"{len(self.visited_urls)+1} / {max}", end=" | ")
        print(f'Crawling: {url} ...')
        self.visited_urls.add(url)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Process the text of the current page
            self.list_of_text_chunks.append({"text":soup.get_text(), "url":url})

            # Extract and process all links on the page
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                if self.is_valid_url(full_url, base_url):
                    self.crawl(full_url, base_url, max=max)

        except requests.exceptions.RequestException as e:
            print(f'Error: {e}') 

    def save_text_chunks(self, output_file):
        output_file = save_to_file_cheker(output_file)
        with open(output_file, "w") as file:
            file.write(json.dumps(self.list_of_text_chunks))

    def open_text_chunks(self, input_file):
        with open(input_file, "r") as file:
            self.list_of_text_chunks = json.loads(file.read())

    def summarize_text_chunks(self, file_name = "summarized_chunks.json", openai = False):
        if not openai:
            # Instantiate the LlamaParser class
            llama_parser = LlamaParser(context_size=8000)

            # Run through all the chunks and summarize them and then save them
            for chunk in tqdm(self.list_of_text_chunks, desc="Summarizing chunks", total=len(self.list_of_text_chunks)):
                chunk["summary"] = llama_parser.query(chunk["text"], echo=False)
        
        else:
            # Test a query
            # Instantiate the OpenAI class
            from openai import OpenAI
            client = OpenAI(
                organization='org-lWc2i4uug3zMNYepkbKKOBcC',
                project='proj_1NnIovGx9DVEXNBjN7gZo9vb',
                )
            
            for chunk in tqdm(self.list_of_text_chunks, desc="Summarizing chunks", total=len(self.list_of_text_chunks)):
                chunk["summary"] = client.chat.completions.create(
                    model="gpt-3.5-turbo-0125",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"Please Extract the important information from the following HTML content that has been converted to text: {chunk["text"]} A: "}
                    ]
                ).choices[0].message.content
        
        # Save the summarized chunks
        self.save_text_chunks(file_name)

    def extract_text_from_url(self, url: str, text: bool):
        '''
        Grab the HTML context from a URL
        '''
        try:
            # Send a GET request to the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if not text:
                return soup.prettify()
            else:
                return soup.get_text()
        except:
            print("Error fetching the URL")
            return None
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract text content from a URL")
    parser.add_argument("--url", "-u", type=str, help="URL to extract text content from")
    parser.add_argument("--max-token-size", "-m", type=int, default=1024, help="Maximum token size for each chunk")
    args = parser.parse_args()

    # Create the scraper class 
    scraper = Scaper()
    
    if args.url:
        scraper.crawl(args.url, args.url,) 
        scraper.save_text_chunks("scraper_output.txt")
        scraper.open_text_chunks("scraper_output.txt")
        scraper.summarize_text_chunks(openai=True)
        scraper.open_text_chunks("summarized_chunks.json")
        for chunk in scraper.list_of_text_chunks:
            print(chunk["summary"])
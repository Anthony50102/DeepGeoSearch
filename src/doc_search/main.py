import argparse
import yaml
from raptor import RetrievalAugmentation 

def build():
    pass

def search(config, search_string):
    tree_path = config['tree path']
    RA = RetrievalAugmentation(tree=tree_path)
    answer = RA.answer_question(question=search_string)
    return answer

def get_config(config_path="config.yml"):
    with open(config_path, "r") as setting:
        config = yaml.load(setting, Loader=yaml.FullLoader)
    return config

def get_args():
    parser = argparse.ArgumentParser(description="Documentation search tool")
    # Create subparsers for the two modes: build and search
    subparsers = parser.add_subparsers(dest="mode", required=True, help='Mode of operation: build or search')
    # Build mode parser
    build_parser = subparsers.add_parser('build', help='Build mode')
    build_parser.add_argument('--config', type=str, required=True, help='Path to the config file')
    # Search mode parser
    search_parser = subparsers.add_parser('search', help='Search mode')
    search_parser.add_argument('--config', type=str, required=True, help='Path to the config file')
    search_parser.add_argument('search_string', type=str, help='String to search for')
    search_parser.add_argument('--size', '-s', type=int, required=False, help='Number of search results to return')
    args = parser.parse_args()
    print(vars(args))
    return vars(args)

if __name__ == "__main__":
    cfg = get_args()
    config = get_config(cfg['config'])
    if cfg['mode'] == 'build': 
        pass
    
    elif cfg['mode'] == 'search':
        print(search(config, cfg['search_string']))
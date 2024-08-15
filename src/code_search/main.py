import argparse
import yaml
from model_handler import ModelHandler
from model_handler_extend import ModelHandlerExtend
from utils.search_engine import *
import pandas as pd
import os
import random
import gc
import json
from collections import OrderedDict


def set_random_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)


def train(config):
    print_config(config)
    set_random_seed(config['random_seed'])
    model = ModelHandler(config)
    model.train()


def test(config, gs=False):
    if not gs:
        print_config(config)
    set_random_seed(config['random_seed'])
    if config['out_dir'] is not None:
        config['pretrained'] = config['out_dir']
        config['out_dir'] = None
    model_handle = ModelHandlerExtend(config)
    model_handle.test()


def build_code_vec_database(config, local=False):
    '''
    Config Requirements: 
    'out_dir' or 'pretrained': Location of saved model
    'index_name': Name of elastic index
    'index_file': Index setup file
    'vector_db': Not entirely sure?
    '''
    print_config(config)
    print(f"{'#'*16} Building index {'remote' if not local else 'locally'} {'#'*16}")
    set_random_seed(config['random_seed'])
    if config['out_dir'] is not None:
        config['pretrained'] = config['out_dir']
        config['out_dir'] = None
    if not local:
        client = Elasticsearch(
            os.getenv('ELASTIC_ENDPOINT'),
            api_key = os.getenv('ELASTIC_API_KEY'),
            timeout=30)
        client.indices.delete(index=config['index_name'], ignore=[404])
        client = create_index(client, config['index_file'])
        model_handle = ModelHandlerExtend(config)
        for file in os.listdir(config['vector_db']):
            if file.endswith('.gz'):
                try:
                    print(file)
                    file_path = os.path.join(config['vector_db'], file)
                    model_handle.prepare_vector_db(file_path)
                    model_handle.build_code_vec_database(client)
                    client.indices.refresh(index=config['index_name'])
                except:
                    continue
        print('built remote index successfully')
    
    else: #TODO
        # Currently just do nothing
        print("Index not saved due to --local argument")



def create_search_engine(config):
    set_random_seed(config['random_seed'])
    if config['out_dir'] is not None:
        config['pretrained'] = config['out_dir']
        config['out_dir'] = None
    model_handle = ModelHandlerExtend(config)
    se = search_engine(model_handle=model_handle, config=config)
    queries = pd.read_csv(config['query_file']).values.tolist()
    se.search(queries)


def create_index(client, index_file):
    with open(index_file) as index_file:
        source = index_file.read().strip()
        client.indices.create(index=config['index_name'], body=source)
    return client


def get_config(config_path="config.yml"):
    with open(config_path, "r") as setting:
        config = yaml.load(setting, Loader=yaml.FullLoader)
    return config


def get_args():
    parser = argparse.ArgumentParser(description="Script with build and search modes")
    # Create subparsers for the two modes: build and search
    subparsers = parser.add_subparsers(dest="mode", required=True, help='Mode of operation: build or search')
    # Build mode parser
    build_parser = subparsers.add_parser('build', help='Build mode')
    build_parser.add_argument('--only-database', action='store_true', required=False, help='Use a pretrained model to create search database')
    build_parser.add_argument('--config', type=str, required=True, help='Path to the config file')
    build_parser.add_argument('--local', '-l', action='store_true', required=False, help='Save elastic index locally instead of sending data stream')
    # Search mode parser
    search_parser = subparsers.add_parser('search', help='Search mode')
    search_parser.add_argument('--config', type=str, required=True, help='Path to the config file')
    search_parser.add_argument('search_string', type=str, help='String to search for')
    search_parser.add_argument('--size', '-s', type=int, required=False, help='Number of search results to return')
    args = parser.parse_args()
    print(vars(args))
    return vars(args)

def print_config(config):
    print("**************** MODEL CONFIGURATION ****************")
    for key in sorted(config.keys()):
        val = config[key]
        keystr = "{}".format(key) + (" " * (24 - len(key)))
        print("{} -->   {}".format(keystr, val))
    print("**************** MODEL CONFIGURATION ****************")



def load_saved_models(dir):
    file_paths = os.listdir(dir)
    records = {}
    for file_path in file_paths:
        if 'Java_Graph2Search' in file_path:
            with open(os.path.join(dir, file_path, 'config.json'), 'r') as f:
                config = json.load(f)
            set_random_seed(config['random_seed'])
            if config['out_dir'] is not None:
                config['pretrained'] = config['out_dir']
                config['out_dir'] = None
            model_handle = ModelHandlerExtend(config)
            format_str = model_handle.test()
            records[file_path] = format_str
    for record in records:
        print(record)
        print(records[record])
        print('***********************************')


if __name__ == '__main__':
    cfg = get_args()
    config = get_config(cfg['config'])
    if cfg['mode'] == 'build' and cfg['only_database'] is False:
        # Train the model, build the database
        train(config)
        test(config)
        build_code_vec_database(config, local=cfg['local'])
    
    elif cfg['mode'] == 'build' and cfg['only_database'] is True:
        # Use a pretrained model to build a new search database
        build_code_vec_database(config, local=cfg['local'])

    elif cfg['mode'] == 'search':
        if not (os.path.exists(config['pretrained'])):
            raise ValueError
        model_handle = ModelHandlerExtend(config)
        se = search_engine(model_handle=model_handle, config=config)
        response = se.search_single_query(cfg['search_string'], search_size=cfg['size'])
        import pprint
        pprint.pprint(response['results'])
        
    else:
        raise ValueError
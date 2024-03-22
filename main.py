import importlib

from config import get_cfg
from utils import check_network, check_exist, remove_if_exist, clean_cache, sleep


def main():
    cfg = get_cfg()
    base_cfg = cfg['base']
    
    # ensure program run once per day
    if base_cfg['run_once_per_day']:
        if check_exist(base_cfg['cache_dir']):
            print('Program is already run today!')
            return
    else:
        remove_if_exist(base_cfg['cache_dir'])
        
    # check network
    retry_time = 0
    while not check_network():
        retry_time += 1
        if retry_time > base_cfg['retry_time']:
            print(f'Network is not available after {retry_time} times retry, exit!')
            return
            
        print('Network is not available, retry in 30 seconds...')
        sleep()

    # clean cache
    clean_cache(base_cfg['cache_dir'], base_cfg['remove_cache_before'])
    
    # run pipeline
    len_pipelines = len(cfg['pipeline'])
    results = []
    for i, pipe in enumerate(cfg['pipeline']):
        clazz = pipe['type']
        module = importlib.import_module('core')
        clazz = getattr(module, clazz)

        type_ = pipe.pop('type')
        print(f'[{i + 1} / {len_pipelines}] Running {type_}...')

        helper = clazz(pipe)
        results = helper.result(results)


if __name__ == '__main__':
    main()

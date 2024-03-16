import importlib

from config import get_cfg
from utils import check_exist, remove_if_exist, clean_cache


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

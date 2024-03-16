import requests

from .base import BaseHelper
from utils import get_random_path, ensure_mkdir


_BASE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


class WebHelper(BaseHelper):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.url = cfg.get('url')
        self.headers = cfg.get('headers', dict())
        self.headers.update(_BASE_HEADERS)
        self.data = cfg.get('data', dict())
    
    def results(self, prev_results=[]):
        prev_results.append(self.get())
        return prev_results

    def get(self, params=dict()):
        params.update(self.data)
        return requests.get(self.url, headers=self.headers, params=params)
    
    def post(self, data=dict()):
        data.update(self.data)
        return requests.post(self.url, headers=self.headers, data=data)
    
    def download(self, url, suffix):
        resp = requests.get(url, headers=self.headers)
        
        path = get_random_path(self.cfg['cache_dir'], suffix)
        ensure_mkdir(path)
        
        print(f'Download to {path}...')
        with open(path, 'wb') as f:
            f.write(resp.content)
        
        return path

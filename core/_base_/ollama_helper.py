import markdown2

from . import WebHelper


class OllamaHelper(WebHelper):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.title = cfg.get('title')
        self.url = self.url + '/api/generate'
        self.prompts = self._prepare_prompts()
        self.data = {
            'model': cfg.get('model'),
            'prompt': self.prompts,
            'stream': False,
        }
        self.show_prompts = cfg.get('show_prompts')
        self.show_think = cfg.get('show_think')
    
    def result(self, prev_results=[]):
        prev_results.append(f'<h2>{self.title}</h2>')
        
        if self.show_prompts:
            prev_results.append(self.prompts.strip() + '\n')
        
        results = self._post_processing_html(markdown2.markdown(self.post().strip()))
        if not self.show_think and '</think>' in results:
            results = results.split('</think>')[1]
            
        prev_results.append(results)
        return prev_results
    
    def post(self, data=dict()):
        response = super().post(data)
        return response.json()['response']
    
    def _prepare_prompts(self):
        raise NotImplementedError

    def _post_processing_html(self, text):
        return text.replace('\n\n', '\n').replace('<hr>\n', '').replace('<hr />\n', '')
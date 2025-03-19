import arxiv
import os
import wordcloud
import uuid

from ._base_.ollama_helper import OllamaHelper
from utils import as_yag_inline


_STOPWORDS_PATH = 'static/stopwords.txt'


class ArXivHelper(OllamaHelper):
    def result(self, prev_results=[]):
        results = super().result(prev_results)
        results.append(self._plot_wordcloud())
        return results
 
    def _prepare_prompts(self):
        results = self._get_arxiv()
        prompts = '最新论文：\n'
        for i, result in enumerate(results):
            prompts += f'({i}) {result.title}\n'
        prompts += '你是一名专业的科研人员，请你根据上述论文，概括近日研究热点，并列出每个热点的相关论文名字：\n'
        return prompts

    def _plot_wordcloud(self):
        results = self._get_arxiv()
        text = ''
        for result in results:
            text += result.title.lower() + ' '
        
        with open(_STOPWORDS_PATH, 'r', encoding='utf-8') as f:
            stopwords = f.read().split('\n')
        
        wc = wordcloud.WordCloud(width=800, height=400, stopwords=stopwords, background_color='white')
        wc.generate(text)
        
        cache_dir = self.cfg.get('cache_dir')
        os.makedirs(cache_dir, exist_ok=True)
        save_path = f'{cache_dir}/{uuid.uuid4()}.png'
        wc.to_file(save_path)
        return as_yag_inline(save_path)

    def _get_arxiv(self):
        client = arxiv.Client()
        search = arxiv.Search(self.cfg.get('query'), 
                              sort_by=arxiv.SortCriterion.SubmittedDate, 
                              max_results=self.cfg.get('max_results'))
        return client.results(search)

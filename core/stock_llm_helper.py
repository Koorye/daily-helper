import akshare as ak
import json
import pandas as pd
import requests
from tabulate import tabulate

from ._base_.ollama_helper import OllamaHelper


_BASE_PROMPT_TEMPLATE = '''你是一个专业的股票分析师，请你预测未来30天{}的走势，并回答以下问题：
1. 未来30天的总体走势是上涨、下跌还是震荡？
2. 未来30天内的上涨、下跌、震荡将占据多少比例？
3. 请你大胆预测未来7,14,30天的具体涨跌幅！
'''


class StockLLMHelper(OllamaHelper):
    def _prepare_prompts(self):
        prompts = ''
        
        if self.cfg.get('add_news'):
            prompts += self._get_stock_news()
            prompts += '\n'
        
        if self.cfg.get('add_index_info'):
            prompts += self._get_index_info()
            prompts += '\n'
        
        prompts += _BASE_PROMPT_TEMPLATE.format(self.cfg.get('index_name'))
        return prompts

    def _get_stock_news(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        html = 'https://np-listapi.eastmoney.com/comm/web/getNewsByColumns?client=web&biz=web_news_col&column=792&order=1&needInteractData=0&page_index=1&page_size=20&req_trace=1740725895564&fields=code,showTime,title,mediaName,summary,image,url,uniqueUrl,Np_dst&types=1,20&callback=jQuery18306921117586611176_1740725895367&_=1740725895565'
        response = requests.get(html, headers=headers)
        data = response.text[response.text.index('(') + 1: -1]
        data = json.loads(data)['data']['list']

        output = '### 最新财经新闻：\n'
        for i, news in enumerate(data):
            output += '({}) {} {}\n'.format(i + 1, news['title'], news['summary'])
        return output

    def _get_index_info(self):
        symbol = self.cfg.get('index_symbol')
        if symbol.startswith('.'):
            df = ak.index_us_stock_sina(symbol)[['date', 'close']].tail(self.cfg.get('days'))
        else:
            df = ak.stock_zh_index_daily(symbol)[['date', 'close']].tail(self.cfg.get('days'))
        
        df['date'] = pd.to_datetime(df['date'])
        df['5day_mean'] = df.close.rolling(5).mean()
        df['10day_mean'] = df.close.rolling(10).mean()

        # replace columns with Chinese
        df.rename(columns={'date': '日期', 'close': '收盘价', '5day_mean': '5日均线', '10day_mean': '10日均线'}, inplace=True)
        df = df.set_index('日期')
        
        output = f'### 近{self.cfg.get("days")}日{self.cfg.get("index_name")}走势：\n' + tabulate(df, headers='keys', tablefmt='pretty') + '\n'
        return output

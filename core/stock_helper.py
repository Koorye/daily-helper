import akshare as ak
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from tqdm import tqdm

from ._base_ import PlotHelper

_DEFAULT_DAYS = 30
_DEFAULT_WIDTH = 8
_DEFAULT_HEIGHT = 3
_DEFAULT_FORECAST_DAYS = 7


class StockHelper(PlotHelper):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.index_symbols = cfg.get('index_symbols', [])
        self.stock_symbols = cfg.get('stock_symbols', [])
        self.days = cfg.get('days', _DEFAULT_DAYS)
    
    def result(self, prev_results=[]):
        index_result = self.prepare_indexs()
        stock_result = self.prepare_stocks()
        prev_results.append('\n<h2>Stock Report</h2>')
        results = super().result(prev_results)
        results.append(index_result)
        results.append(stock_result)
        return results
    
    def prepare_indexs(self):
        result = ''
        
        for symbol in tqdm(self.index_symbols, desc='Preparing indexs'):
            try:
                if symbol.startswith('.'):
                    df = ak.index_us_stock_sina(symbol)[['date', 'close']].tail(2 * self.days)
                else:
                    df = ak.stock_zh_index_daily(symbol)[['date', 'close']].tail(2 * self.days)
                    
                symbol = self.index_symbols[symbol]
                df, content = self.process_df(df)
                result += f'<b>{symbol}</b>: {content}\n'
                df = self.forecast(df)
                df = df.tail(self.days + _DEFAULT_FORECAST_DAYS)

                df = pd.melt(df, id_vars='date', value_vars=['close', '5day_mean', '10day_mean', 'forecast'],
                            var_name='type', value_name='price')
                self.add_prop(dict(df=df, x='date', y='price', type='line', color='type',
                                   xlab='日期', ylab='价格', title=f'{symbol}', 
                                   legend_alias={'close': '收盘价', '5day_mean': '5日均线', 
                                                 '10day_mean': '10日均线', 'forecast': '预测走势'},
                                   width=_DEFAULT_WIDTH, height=_DEFAULT_HEIGHT))
            except:
                result += f'Failed to get {symbol}!\n'
        
        return result
            
    def prepare_stocks(self):
        result = ''

        for symbol in tqdm(self.stock_symbols, desc='Preparing stocks'):
            try:
                df = ak.stock_zh_a_daily(symbol)[['date', 'close']]

                symbol = self.index_symbols[symbol]
                df, content = self.process_df(df)
                result += f'<b>{symbol}</b>: {content}\n'
                df = self.forecast(df)
                df = df.tail(self.days + _DEFAULT_FORECAST_DAYS)

                df = pd.melt(df, id_vars='date', value_vars=['close', '5day_mean', '10day_mean', 'forecast'],
                            var_name='type', value_name='price')
                self.add_prop(dict(df=df, x='date', y='price', type='line', color='type',
                                   xlab='日期', ylab='价格', title=f'{symbol}', 
                                   legend_alias={'close': '收盘价', '5day_mean': '5日均线', 
                                                 '10day_mean': '10日均线', 'forecast': '预测走势'},
                                   width=_DEFAULT_WIDTH, height=_DEFAULT_HEIGHT))
            except:
                result += f'Failed to get {symbol}!\n'
        
        return result

    def process_df(self, df):
        df['date'] = pd.to_datetime(df['date'])
        df['5day_mean'] = df.close.rolling(5).mean()
        df['10day_mean'] = df.close.rolling(10).mean()

        if (df['close'] < df['10day_mean']).tolist()[-1]:
            return df, '<span style="color: red;">今日价格低于10日均线! </span>'
        elif (df['close'] < df['5day_mean']).tolist()[-1]:
            return df, '<span style="color: orange;">今日价格低于5日均线! </span>'
        else:
            return df, '今日价格安全。'

    def forecast(self, df):
        # forecast with ARIMA
        model = ARIMA(df['close'], order=(4, 2, 0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=_DEFAULT_FORECAST_DAYS)
        pred_df = pd.DataFrame({'date': pd.date_range(start=df['date'].max() + pd.Timedelta(days=1), 
                                                      periods=_DEFAULT_FORECAST_DAYS, freq='D'), 
                                'forecast': forecast})
        df = pd.concat([df, pred_df], axis=0)
        return df

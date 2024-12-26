import pyweathercn
import pandas as pd

from ._base_ import PlotHelper

_DEFAULT_CITY = '北京'
_DEFAULT_WIDTH = 8
_DEFAULT_HEIGHT = 3
_WEATHER_TO_ENG = {'晴': 'Sunny', '多云': 'Cloudy', '阴': 'Overcast', 
                   '阵雨': 'Shower', '小雨': 'Light Rain', '中雨': 'Moderate Rain', 
                   '大雨': 'Heavy Rain', '暴雨': 'Storm', '雾': 'Fog', 
                   '霾': 'Haze', '雪': 'Snow', '雨夹雪': 'Sleet', '小雪': 'Light Snow',
                   '中雪': 'Moderate Snow', '大雪': 'Heavy Snow', '暴雪': 'Blizzard',
                   '雷阵雨': 'Thunder shower'}


class WeatherHelper(PlotHelper):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.city = cfg.get('city', _DEFAULT_CITY)
        self.tips = cfg.get('tips', [])
        
    def result(self, prev_results=[]):
        prev_results.append('\n<h2>Weather Report</h2>')
        result = self.prepare_weather()
        prev_results = super().result(prev_results)
        prev_results.append(result)
        return prev_results
    
    def prepare_weather(self):
        try:
            data = pyweathercn.Weather(self.city).data
        except:
            return 'Failed to get weather data!\n'

        aqi = int(data['aqi'].split(' ')[0])
        max_temp, min_temp = self._split_temp(data['temp'])
        aqi, max_temp, min_temp = self._colorize_important(aqi, max_temp, min_temp)
        tips = self._order_tips(data['tip'])
        self._process_forecast(data['forecast'])

        return f'<b>最高温度</b>: {max_temp}℃\n<b>最低温度</b>: {min_temp}℃\n<b>空气质量</b>: {aqi}\n' \
              + '\n'.join([f'<b>{k}</b>: {v}' for k, v in tips.items()])
        
    def _order_tips(self, tips):
        ordered_tips = {}
        
        for tip in tips.split('\n'):
            s = tip.split('：')
            if len(s) == 2 and s[0] in self.tips:
                ordered_tips[s[0]] = s[1]
        
        return ordered_tips

    def _split_temp(self, temp):
        return [int(x) for x in temp[:-1].split('/')]
    
    def _colorize_important(self, aqi, max_temp, min_temp):
        if aqi > 200:
            aqi = f'<span style="color: red;">{aqi}</span>'
        if max_temp > 35:
            max_temp = f'<span style="color: red;">{max_temp}</span>'
        if min_temp < 0:
            min_temp = f'<span style="color: blue;">{min_temp}</span>'
        return aqi, max_temp, min_temp
    
    def _process_forecast(self, forecast):
        df = pd.DataFrame(forecast)
        df['date'] = df['date'].apply(lambda x: x.split(' ')[0])
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        types = [str(date.strftime('%m-%d')) + ' ' + type_
                 for date, type_ in zip(df['date'], df['type'])]
        
        df['max_temp'] = df['temp'].apply(lambda x: self._split_temp(x)[0])
        df['min_temp'] = df['temp'].apply(lambda x: self._split_temp(x)[1])
        temp_df = df[['date', 'max_temp', 'min_temp']]
        temp_df = pd.melt(temp_df, id_vars='date', value_vars=['max_temp', 'min_temp'],
                          var_name='type', value_name='temp')
        self.add_prop(dict(df=temp_df, x='date', y='temp', 
                           xticklabels=types, xticktype='datetime',
                           type='line', color='type',
                           xlab='天气', ylab='温度(℃)', title='天气预报',
                           legend_alias={'max_temp': '最高温度', 'min_temp': '最低温度'},
                           width=_DEFAULT_WIDTH, height=_DEFAULT_HEIGHT))

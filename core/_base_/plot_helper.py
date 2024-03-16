import copy
from plotnine import *
from tqdm import tqdm

from .base import BaseHelper
from utils import get_random_path, ensure_mkdir, as_yag_inline

_DEFAULT_SUFFIX = 'jpg'

_DEFAULT_PLOT_PROP = dict(
    df=None,
    x=None,
    y=None,
    xticklabels=None,
    xticktype=None,
    type='line',
    color=None,
    xlab='X',
    ylab='Y',  
    title=None,
    width=8,
    height=6,
)


class PlotHelper(BaseHelper):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.props = []
        self.cache_dir = cfg['cache_dir']
    
    def add_prop(self, prop):
        default_prop = copy.deepcopy(_DEFAULT_PLOT_PROP)
        default_prop.update(prop)
        self.props.append(default_prop)
    
    def result(self, prev_results=[]):
        if len(self.props) == 0:
            prev_results.append('Failed to get data!')
            print('Failed to get data!')
            return prev_results
        
        plots = []
        
        for prop in tqdm(self.props, desc='Plotting'):
            if prop['type'] == 'line':
                plots.append(self.line(prop))
            elif prop['type'] == 'bar':
                plots.append(self.bar(prop))
        
        paths = self.save(plots)
        prev_results += paths
        return prev_results
    
    def line(self, prop):
        p = (
            ggplot(prop['df'], aes(prop['x'], prop['y'], color=prop['color'])) 
            + geom_line() 
            + geom_point()
            + labs(x=prop['xlab'], y=prop['ylab'], title=prop['title'], color='')
            + theme_seaborn()
            + theme(axis_text_x=element_text(rotation=45, hjust=1))
        )
        return self.custom_ticks(p, prop)

    def bar(self, prop):
        p = (
            ggplot(prop['df'], aes(prop['x'], prop['y'], fill=prop['color']))
            + geom_col(position='dodge')
            + labs(x=prop['xlab'], y=prop['ylab'], title=prop['title'])
            + theme_seaborn()
            + theme(axis_text_x=element_text(rotation=45, hjust=1))
        )
        return self.custom_ticks(p, prop)
    
    def custom_ticks(self, plot, prop):
        if prop['xticklabels'] is not None:
            if prop['xticktype'] == 'continuous':
                plot = plot + scale_x_continuous(labels=prop['xticklabels'])
            elif prop['xticktype'] == 'discrete':
                plot = plot + scale_x_discrete(labels=prop['xticklabels'])
            elif prop['xticktype'] == 'datetime':
                plot = plot + scale_x_datetime(labels=prop['xticklabels'])
        return plot
    
    def save(self, plots):
        paths = []

        for p, prop in tqdm(list(zip(plots, self.props)), desc='Saving plots'):
            path = get_random_path(self.cache_dir, _DEFAULT_SUFFIX)
            ensure_mkdir(path)

            p.save(path, width=prop['width'], height=prop['height'])
            paths.append(as_yag_inline(path))

        return paths

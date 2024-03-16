class BaseHelper(object):
    def __init__(self, cfg):
        self.cfg = cfg
    
    def result(self, prev_results=[]):
        return prev_results

    def update_if_not_none(self, d, key, value):
        if value is not None:
            d[key] = value

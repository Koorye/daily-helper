class SummaryHelper:
    def __init__(self, cfg):
        self.generate_toc = cfg.get('generate_toc', False)
    
    def result(self, prev_results=[]):
        # find all titles
        titles, title_indexs = [], []
        for idx, result in enumerate(prev_results):
            if '<h2>' in result:
                titles.append(result)
                title_indexs.append(idx)
        
        # add line before title
        for idx in title_indexs[::-1]:
            prev_results.insert(idx, '<hr>')
        
        # add toc
        if self.generate_toc:
            toc = '<h2>目录</h2>'
            for idx, title in enumerate(titles):
                toc += f'<a href="#{idx}">{title}</a>'
            prev_results.insert(0, toc)

        return prev_results

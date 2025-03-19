from ._base_ import WebHelper
from utils import as_yag_inline


class BingWallPaperHelper(WebHelper):
    def __init__(self, cfg):
        super().__init__(cfg)

    def result(self, prev_results=[]):
        prev_results.append('<h2>每日必应壁纸</h2>')
        data = self.get().json()
        img_url = data['url']
        try:
            path = self.download(img_url, 'jpg')
            prev_results.append(as_yag_inline(path))
            prev_results.append(data['copyright'])
        except:
            prev_results.append('Failed to download image!\n')
        return prev_results

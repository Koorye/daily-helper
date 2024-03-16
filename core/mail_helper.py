import yagmail
from tqdm import tqdm

from ._base_ import BaseHelper


class MailHelper(BaseHelper):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.client = yagmail.SMTP(
            user=cfg['user'],
            password=cfg['password'],
            host=cfg['host'],
            port=cfg['port'],
        )
        self.tos = cfg['to']
        self.subject = cfg['subject']

    def result(self, prev_results=[]):
        for to in tqdm(self.tos, desc='Sending mails'):
            self.client.send(to, self.subject, prev_results)
            self.client.close()
        print('Mail sent to {}!'.format('/'.join(self.tos)))
        return []

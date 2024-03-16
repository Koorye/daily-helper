import datetime
import os
import os.path as osp
import shutil
import uuid
import yagmail


def as_yag_inline(path):
    return yagmail.inline(path)


def check_exist(path):
    return osp.exists(path)


def clean_cache(path, days=7):
    if not check_exist(path):
        return
    for filename in os.listdir(path):
        f = osp.join(path, filename)
        if osp.isdir(f):
            mtime = osp.getmtime(f)
            if (datetime.datetime.now() - datetime.datetime.fromtimestamp(mtime)).days >= days:
                os.remove(f)


def get_parent_path(path):
    return '/'.join(path.replace('\\', '/').split('/')[:-1])


def get_random_path(dir_, suffix):
    return osp.join(dir_, str(uuid.uuid4()) + '.' + suffix)


def ensure_mkdir(path):
    path = get_parent_path(path)
    os.makedirs(path, exist_ok=True)


def remove_if_exist(dir_):
    shutil.rmtree(dir_, ignore_errors=True)


def today():
    return datetime.datetime.now().strftime('%Y-%m-%d')
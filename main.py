from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
from pathlib import Path
import pandas as pd
import time
import requests
import configparser
import random
import re
import sys
import logger

config = configparser.ConfigParser()
config.read('config.ini')

HOST = 0
PORT = 1
PROTOCOL = 2


def d(proxy, logger):
    with requests.Session() as s:
        s.proxies = {proxy[PROTOCOL]: '{protocol}://{host}:{port}'.format(
            protocol=proxy[PROTOCOL],
            host=proxy[HOST],
            port=proxy[PORT]
        )}
        s.auth = HTTPBasicAuth(config.get('d', 'basic_username'), config.get('d', 'basic_password'))
        host = config.get('d', 'host')

        r = s.post('https://{}/index.php'.format(host), data={
            'mode': 'authorize',
            'username': config.get('d', 'post_username'),
            'password': config.get('d', 'post_password')
        })

        if '200'.__eq__(r.status_code):
            r = s.get('https://{}/index.php?mode=stat'.format(host))

            soup = BeautifulSoup(r.content, 'html.parser')
            table = soup.find_all('table', attrs={'class': 'tbl c'})[0]

            df = pd.read_html(str(table))

            file = config.get('main', 'data_path') + '/' + time.strftime(config.get('d', 'file_format'))

            with open(file, 'w') as f:
                f.write(df[0].to_string())
                logger.info('{}, write to: {}'.format(host, file))


def p(proxy, logger):
    with requests.Session() as s:
        s.proxies = {proxy[PROTOCOL]: '{protocol}://{host}:{port}'.format(
            protocol=proxy[PROTOCOL],
            host=proxy[HOST],
            port=proxy[PORT]
        )}
        host = config.get('p', 'host')

        r = s.post('https://{}/index.php'.format(host), data={
            'page': 'authorize',
            'pagetogo': '',
            'username': config.get('p', 'post_username'),
            'password': config.get('p', 'post_password')
        })

        if '200'.__eq__(r.status_code):
            r = s.get('https://{}/index.php?page=date'.format(host))

            soup = BeautifulSoup(r.content, 'html.parser')
            table = soup.find_all('table', attrs={'class': 'table'})[0]

            df = pd.read_html(str(table))

            file = config.get('main', 'data_path') + '/' + time.strftime(config.get('p', 'file_format'))

            with open(file, 'w') as f:
                f.write(df[0].to_string())
                logger.info('{}, write to: {}'.format(host, file))


def random_line(afile):
    line = next(afile)

    for num, aline in enumerate(afile, 2):
        if random.randrange(num): continue
        line = aline

    return line


if __name__ == '__main__':
    Path(config.get('main', 'data_path')).mkdir(parents=True, exist_ok=True)

    try_count = int(config.get('main', 'try_count'))
    logger = logger.init_logger(__name__, testing_mode=False)
    proxy = None
    skip = False

    while try_count > 0:
        try_count -= 1

        with open(config.get('main', 'proxy_file'), 'r') as f:
            line = random_line(f)
            proxy = re.split(r'\s+|\t+', line)

        logger.warning('Try: {try_count}, Proxy: {proxy}'.format(try_count=3 - try_count, proxy=proxy))

        try:
            if len(sys.argv) == 2:
                if 'd'.__eq__(sys.argv[1]):
                    skip = True
                    d(proxy, logger)
                elif 'p'.__eq__(sys.argv[1]):
                    skip = True
                    p(proxy, logger)

            if not skip:
                d(proxy, logger)
                p(proxy, logger)
        except requests.exceptions.ProxyError as err:
            continue
        except Exception as err:
            logger.error('Exception: {}'.format(err))

        break

    if try_count == 0:
        logger.error('The number of attempts has been exhausted. Change the list of proxy servers or check your Internet connection')
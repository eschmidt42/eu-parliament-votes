# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_downloading_pdfs.ipynb (unless otherwise specified).

__all__ = ['URL', 'PDF_PATH', 'identify_links_for_pdfs', 'download_file', 'collect_multiple_files']

# Cell
from pathlib import Path
import requests
import re
from bs4 import BeautifulSoup
import typing
import time
import tqdm
import sys
from loguru import logger

# Cell
URL = 'https://www.europarl.europa.eu/plenary/en/votes.html?tab=votes'
PDF_PATH = Path("../pdfs")

# Cell
def identify_links_for_pdfs(url:str, bs_parser:str='lxml'):
    'There are RCV (Roll Call Vote) and VOT PDF files. Links for both are extracted.'

    with requests.Session() as s:
        res = s.get(url)

    soup = BeautifulSoup(res.text, features=bs_parser)

    elements_with_pdf = soup.find_all(name='a', attrs={'class':'link_pdf'})
    pattern = re.compile(r'RCV\w*\.pdf')

    rcv_pdfs = [element['href'] for element in elements_with_pdf if pattern.search(element['href'])]
    vot_pdfs = [element['href'] for element in elements_with_pdf if pattern.search(element['href']) is None]

    return rcv_pdfs, vot_pdfs

# Cell
def download_file(link:str, file_dir:Path=PDF_PATH):
    'Given a valid URL a file is downloaded.'

    filename = link.split('/')[-1]

    r = requests.get(link, allow_redirects=True)

    logger.debug(f'Writing to {file_dir/filename}')
    with open(file_dir/filename, 'wb') as f:
        f.write(r.content)

# Cell
def collect_multiple_files(links:typing.List[str], file_dir:Path=PDF_PATH, dt:float=.5):
    for link in tqdm.tqdm(links, total=len(links), desc='File'):
        time.sleep(dt)
        download_file(link, file_dir)
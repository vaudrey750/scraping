from requests import get
from bs4 import BeautifulSoup

class BaseFffScraping:
    def __init__(self, url: str):
        self.page = get(url)
        self.soup = BeautifulSoup(self.page.content, "lxml")

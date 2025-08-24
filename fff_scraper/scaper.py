from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def init_scraper(headless: bool = True, disable_gpu: bool = True, window_size:str = "1920,1080"):
    # Configuration du mode headless
    options = Options()
    if headless:
        options.add_argument("--headless")           # Ne pas afficher la fenêtre
    if disable_gpu:
        options.add_argument("--disable-gpu")        # Option souvent nécessaire sous Windows
    options.add_argument("--window-size={window_size}")  # Taille par défaut pour éviter certains bugs

    driver = webdriver.Chrome(options=options) 
    return driver



import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pprint as pp

class RMPScraper:

    def __init__ (self, id: int = 1003, university: str = "Texas A&M University"):

        options = uc.ChromeOptions() # set up the Chrome options 
        options.add_argument("--disable-gpu") # disable the GPU 
        options.add_argument("--headless=new") # run the browser in headless mode 
        options.add_argument("--ignore-certificate-errors") # ignore certificate errors
        options.add_argument("--ssl-version-max=TLSv1.2") # set the SSL version to the latest version
        options.add_argument("--disable-dev-shm-usage")  # disable the dev shm usage 
        options.add_argument("--no-sandbox")  # disable the sandbox
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ) # set the user agent to prevent detection
        options.add_argument("--disable-extensions") # disable any extensions that the browser may have
        # options.add_argument("--allow-running-insecure-content") # allow running insecure content
        # options.add_argument("--disable-web-security") # disable web security 

        self.driver = uc.Chrome(options=options, headless=True) # create a new instance of the Chrome driver
        self.id = id 
        self.university = university    

        print("Scraper initialized.")

    

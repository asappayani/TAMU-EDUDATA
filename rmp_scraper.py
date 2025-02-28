import time
import re
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class RMPScraper:
    """
    A class to scrape RateMyProfessor data. We need to use Selenium because RMP is a dynamic website that uses JavaScript to load data.
    """
    def __init__(self, id):
        """ Initializes the RMPScraper class and sets up the Chrome driver """

        options = uc.ChromeOptions() # set up the Chrome options which in simple terms is the settings of the browser that you are using 
        options.add_argument("--disable-gpu")  
        options.add_argument("--headless=new")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-web-security")
        options.add_argument("--ssl-version-max=TLSv1.2")
        options.add_argument("--disable-dev-shm-usage")  # Improves performance in headless mode
        options.add_argument("--no-sandbox")  # Required in some environments
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        self.driver = uc.Chrome(options=options, headless=True) # create a new instance of the Chrome driver
        self.driver.__del__ = lambda: None
        self.id = id

        print("Driver initialized")

    def get_rmp_rating(self, prof, university="Texas A&M University"):
        search_url = f"https://www.ratemyprofessors.com/search/professors/{self.id}?q={prof.replace(" ", "%20")}"
        self.driver.get(search_url) # open the search URL
        
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="/professor/"]')) # wait for the page to load
            ) 

            prof_names = self.driver.find_elements(By.CSS_SELECTOR, ".CardName__StyledCardName-sc-1gyrgim-0") # get all the prof names
            prof_ratings = self.driver.find_elements(By.CSS_SELECTOR, ".CardNumRating__CardNumRatingNumber-sc-17t4b9u-2") # get all the prof ratings
            prof_universities = self.driver.find_elements(By.CSS_SELECTOR, ".CardSchool__School-sc-19lmz2k-1") # get all the prof universities

            for name, rating, uni in zip(prof_names, prof_ratings, prof_universities):
                if prof.lower() in name.text.lower().strip() and university.lower() in uni.text.lower().strip():
                    return rating.text.strip() or "No rating"

        except:
            return "N/A"
        
        return "No professors found."

    def deactivate(self):
        """ Safely deactivates the Chrome driver to avoid destructor errors """
        if hasattr(self, "driver") and self.driver:
            try:
                self.driver.quit()
                self.driver = None
                print("Driver successfully closed.")
            except Exception as e:
                print(f"Error closing driver: {e}")

        del self.driver
            

if __name__ == "__main__":
    scraper = RMPScraper(1003)

    professors = ["AMY A", "SANG L", "ALI K"]
    print(scraper.get_rmp_rating("AMY A"))

    scraper.deactivate()
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pprint as pp
from .name_handler import process_professor_name, get_name_match_score, get_department_name_match_score
from typing import Union

class RMPScraper:

    def __init__(self, university_id: int = 1003, university: str = "Texas A&M University"):
        """ Initializes the RMPScraper class and sets up the Chrome drive. """

        options = uc.ChromeOptions() # set up the Chrome options 
        options.add_argument("--disable-gpu") # disable the GPU 
        options.add_argument("--headless=new") # run the browser in headless mode 
        options.add_argument("--ignore-certificate-errors") # ignore certificate errors
        options.add_argument("--ssl-version-max=TLSv1.2") # set the SSL version to the latest version
        options.add_argument("--disable-dev-shm-usage")  # disable the dev shm usage 
        options.add_argument("--no-sandbox")  # disable the sandbox
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ) # set the user agent to prevent detection
        options.add_argument("--disable-extensions") # disable any extensions that the browser may have

        self.driver = uc.Chrome(options=options, headless=True) # create a new instance of the Chrome driver
        self.university_id = university_id 
        self.university = university    

        print("Scraper initialized.")


    def get_professor_rating(self, professor_name: str, department: str) -> Union[float, str]:
        """ Returns the rating of the professor. """

        search_url = f"https://www.ratemyprofessors.com/search/professors/{self.university_id}?q={process_professor_name(professor_name, query=True).replace(' ', '%20')}"
        self.driver.get(search_url) 

        # wait for the page to load
        WebDriverWait(self.driver, 4).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="/professor/"]'))) 

        # get the professor information off the page
        rmprof_names = self.driver.find_elements(By.CSS_SELECTOR, ".CardName__StyledCardName-sc-1gyrgim-0") 
        rmprof_ratings = self.driver.find_elements(By.CSS_SELECTOR, ".CardNumRating__CardNumRatingNumber-sc-17t4b9u-2")
        rmprof_universities = self.driver.find_elements(By.CSS_SELECTOR, ".CardSchool__School-sc-19lmz2k-1") 
        rmprof_departments = self.driver.find_elements(By.CSS_SELECTOR, ".CardSchool__Department-sc-19lmz2k-0") 

        for rmprof_name, rmprof_rating, rmprof_university, rmprof_department in zip(rmprof_names, rmprof_ratings, rmprof_universities, rmprof_departments):
            # get the match scores
            name_match_score = get_name_match_score(professor_name, rmprof_name.text) 
            department_match_score = get_department_name_match_score(department, rmprof_department.text)

            if name_match_score >= 85 and (department_match_score >= 85 or department_match_score == 0) and \
                self.university.lower() in rmprof_university.text.lower():
                print(f"Prof Name: {professor_name} | RMP Name: {rmprof_name.text} | Score: {name_match_score}")
                return float(rmprof_rating.text.strip())
            
        return "No rating found." 
            
if __name__ == "__main__":
    scraper = RMPScraper()
    print(scraper.get_professor_rating("AUSTIN A", "Mathematics"))

            

            


    




   

    

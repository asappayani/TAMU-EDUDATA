import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pprint as pp
import rapidfuzz

class RMPScraper:

    #* """A class to scrape RateMyProfessor data"""

    def __init__(self, id, university): #* constructor

        #* """ Initializes the RMPScraper class and sets up the Chrome driver """

        options = uc.ChromeOptions() # set up the Chrome options which in simple terms is the settings of the browser that you are using 
        options.add_argument("--disable-gpu")  
        options.add_argument("--headless=new")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-web-security")
        options.add_argument("--ssl-version-max=TLSv1.2")
        options.add_argument("--disable-dev-shm-usage")  
        options.add_argument("--no-sandbox")  
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36") # set the user agent to prevent detection
        options.add_argument("--disable-extensions")

        self.driver = uc.Chrome(options=options, headless=True) # create a new instance of the Chrome driver
        self.id = id 
        self.university = university
        self.college_departments = self.__get_valid_departments()

        print("Driver initialized")

    def __get_valid_departments(self): #* private method
        """ Returns a list of valid departments """
        try:
            search_url = f"https://www.tamu.edu/academics/colleges-schools/index.html"
            self.driver.get(search_url) # open the search URL
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".row.aux-container--fluid-mw"))
            )           

            schools = [school.get_attribute("href") for school in self.driver.find_elements(By.XPATH, "//aside/nav/ul/li/a")]
            departments = set()

            
            for school in schools:
                self.driver.get(school)
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".row.aux-container--fluid-mw"))
                )

                departments.update([department.text.lower() for department in self.driver.find_elements(By.CSS_SELECTOR, 'td[data-label="Department"]')])
            
            return departments

        except Exception as e:
            print(f"Error: {e}")
            return None
    
    # TODO: Implement a better name matching algorithm
    def __name_match_score(self, prof_name, rmp_name):
        """ Returns the match score of the professor name and the RateMyProfessor name """
        pass

    # TODO: Implement a better department checking algorithm
    def __check_valid_department(self, department, valid_departments):
        """ Checks if the departments are valid """
        pass

    def get_rmp_rating(self, prof, department=None):
        """ Gets the RateMyProfessor rating for a professor in a specific department """

        search_url = f"https://www.ratemyprofessors.com/search/professors/{self.id}?q={prof.replace(' ', '%20')}"
        self.driver.get(search_url) # open the search URL
        
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="/professor/"]')) # wait for the page to load
            ) 

            prof_names = self.driver.find_elements(By.CSS_SELECTOR, ".CardName__StyledCardName-sc-1gyrgim-0") # get all the prof names
            prof_ratings = self.driver.find_elements(By.CSS_SELECTOR, ".CardNumRating__CardNumRatingNumber-sc-17t4b9u-2") # get all the prof ratings
            prof_universities = self.driver.find_elements(By.CSS_SELECTOR, ".CardSchool__School-sc-19lmz2k-1") # get all the universities of the profs
            prof_departments = self.driver.find_elements(By.CSS_SELECTOR, ".CardSchool__Department-sc-19lmz2k-0") # get all the departments of the profs

            # TODO: Implement a better name matching algorithm
            if len(prof.split()) <= 2: # check if the professor has a middle name or a 2 word last name
                prof_fname, prof_lname = prof.split(" ")[0].lower(), prof.split(" ")[-1].lower()
            else:
                prof_lname, prof_fname = " ".join(prof.split(" ")[0:-2]).lower(), prof.split(" ")[-1].lower()

            for name, rating, uni, dep in zip(prof_names, prof_ratings, prof_universities, prof_departments):
                rmp_fname, rmp_lname = name.text.strip().split(" ")[0].lower(), name.text.strip().split(" ")[1].lower()

                # print(f"RMP: {rmp_fname} {rmp_lname} | {prof_fname} {prof_lname} | {uni.text} | {dep.text}")
            if (prof_fname in rmp_fname and 
                prof_lname in rmp_lname and 
                self.university.lower() in uni.text.strip().lower() and 
                (not department or department.lower() in dep.text.strip().lower())):

                return rating.text.strip()     

        except Exception as e:
            print(f"Error: {e}")
            return "N/A"
        
        return "Rating N/A"
            
if __name__ == "__main__":
    scraper = RMPScraper(994, "Tarleton State University")
    pp.pprint(scraper.college_departments)
    # print(scraper.get_rmp_rating("ABBOTT SHANNON", "English"))
    # print("End of program")
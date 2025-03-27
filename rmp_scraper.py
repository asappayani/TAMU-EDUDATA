import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pprint as pp
from rapidfuzz import fuzz

class RMPScraper:

    """A class to scrape RateMyProfessor data"""

    def __init__(self, id, university): # constructor

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

    def __get_valid_departments(self) -> set: # private method
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
    
    def process_professor_name(self, professor_name: str, format_name: bool = False, dash_handler: bool = False) -> str:
        if len(professor_name.strip()) <= 2: # if the professor name is empty or has only one character
            print(f'Professor name: {professor_name}')
            raise ValueError("process_professor_name: Professor name is invalid length")
        
        if ' ' not in professor_name: # if the professor name doesn't have a space
            print(f"Professor name: {professor_name}")
            raise ValueError("process_professor_name: Professor name is invalid, no space found")
        
        professor_name_parts = professor_name.lower().strip().split()
        
        if format_name and dash_handler: # return the first initial and the name before the dash
            return f"{professor_name_parts[-1]} {professor_name_parts[0].split('-')[0]}" 
            
        elif format_name: # return the first initial and the last name
            return f"{professor_name_parts[-1]} {' '.join(professor_name_parts[:-1])}" 
        
        else: # return the professor name as is
            return professor_name.lower().strip()

    # TODO: Implement a better name matching algorithm, dash handling (rmp doesn't register the dash when searching, find workaround), and two word last name handling
    # TODO: also, the prof name on RMP may not even include the middle name or one of the words in the last name so we need to account for that

    def get_name_match_score(self, prof_name: str, rmp_name: str) -> float: 
        """ Returns the match score between the professor name and the RateMyProfessor name """
        try:
            prof_name = self.process_professor_name(prof_name, format_name=True) # format the professor name, keeps the dash if it exists
            rmp_name = self.process_professor_name(rmp_name)

            prof_first_initial, prof_last_name = prof_name.split(" ")[0], ' '.join(prof_name.split(" ")[1:])
            rmp_first_name, rmp_last_name = rmp_name.split(" ")[0], ' '.join(rmp_name.split(" ")[1:])

            if prof_first_initial != rmp_first_name[0]:
                return 0.0
            
            if len(prof_last_name) < len(rmp_last_name) or len(rmp_last_name) < len(prof_last_name):
                return fuzz.partial_ratio(prof_last_name, rmp_last_name)    

            return fuzz.ratio(prof_last_name, rmp_last_name)
            
        except ValueError as e: 
            if e == "process_professor_name: Professor name is invalid, no space found": # the name passed might just be the last name, handle that before returning anything
                rmp_last_name = rmp_name.split(" ")[1]

                return fuzz.ratio(prof_name, rmp_last_name)
            
            else:
                print(f"Error: {e}")
                return 0.0

    # TODO: Implement a better department checking algorithm
    def check_valid_department(self, department: str, valid_departments: set) -> bool:
        """ Checks if the departments are valid """
        for valid_department in valid_departments:
            if fuzz.partial_ratio(department, valid_department) >= 90:
                return True
        
        return False

    def get_rmp_rating(self, professor: str, department: str = None) -> str:
        """ Gets the RateMyProfessor rating for a professor in a specific department """

        try:
            if '-' in professor: # handle the case where the professor name has a dash
                professor_query = self.process_professor_name(professor, format_name=True, dash_handler=True)
            else:
                professor_query = self.process_professor_name(professor, format_name=True)
        except ValueError as e:
            print(f"Error: {e}")
            return "Rating N/A"

        # open the web page
        search_url = f"https://www.ratemyprofessors.com/search/professors/{self.id}?q={professor_query.replace(' ', '%20')}"
        self.driver.get(search_url) 
        
        try:
            WebDriverWait(self.driver, 3).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="/professor/"]')) ) # wait for the page to load

            rmp_prof_names = self.driver.find_elements(By.CSS_SELECTOR, ".CardName__StyledCardName-sc-1gyrgim-0") # get all the prof names
            rmp_prof_ratings = self.driver.find_elements(By.CSS_SELECTOR, ".CardNumRating__CardNumRatingNumber-sc-17t4b9u-2") # get all the prof ratings
            rmp_prof_universities = self.driver.find_elements(By.CSS_SELECTOR, ".CardSchool__School-sc-19lmz2k-1") # get all the universities of the profs
            rmp_prof_departments = self.driver.find_elements(By.CSS_SELECTOR, ".CardSchool__Department-sc-19lmz2k-0") # get all the departments of the profs
            

            for name, rating, uni, dep in zip(rmp_prof_names, rmp_prof_ratings, rmp_prof_universities, rmp_prof_departments):


                name_match_score = self.get_name_match_score(professor, name.text)
                is_department_valid = self.check_valid_department(dep.text.strip().lower(), self.college_departments)

                if (name_match_score > 75 and 
                    self.university.lower() in uni.text.strip().lower() and 
                    (not is_department_valid or is_department_valid and department.lower() in dep.text.strip().lower())):  # Adjusted to ensure department check works

                    print(f"Prof Name: {professor} RMP Name: {name.text}, Score: {name_match_score}")
                    return rating.text.strip()     

        except Exception as e:
            print(f"Error: {e}")
            return "N/A"
        
        return "Rating N/A"
            
if __name__ == "__main__":
    scraper = RMPScraper(1003, "Texas A&M University")
    print(scraper.get_name_match_score(scraper.process_professor_name("SANJUAN MUNOZ J", format_name=True), scraper.process_professor_name("J SANJUAN")))

    #print(scraper.get_rmp_rating("BECKER A", "INFORMATION & OPERATIONS MGMT")
    # print(scraper.process_professor_name("GUTIERREZ-OSUNA R", format_name=True, dash_handler=True))
    # print(scraper.process_professor_name("CRUZADO GARCIA A", format_name=True))
    #pp.pprint(scraper.college_departments)
    # print(scraper.get_rmp_rating("ABBOTT SHANNON", "English"))
    # print("End of program")
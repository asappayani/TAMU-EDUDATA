import pdfplumber 
import re
from pprint import pp
from pymongo import MongoClient
import rmp_scraper

client = MongoClient("mongodb://localhost:27017/")
db = client["tamu_gpa"]
collection = db["gpa_distribution"]

# header regex pattern
header_pattern = re.compile(
    r"FOR\s+(?P<semester>[A-Z]+)\s+(?P<year>\d{4})\s+.*?"
    r"COLLEGE:\s*(?P<college>[A-Z &]+(?: [A-Z]+)*)\s+"
    r"DEPARTMENT:\s*(?P<department>[A-Z &]+(?: [A-Z]+)*)\s+TOTAL",
    re.DOTALL
)

# course regex pattern
course_pattern = re.compile(
    r"(?P<course>[A-Z]+-\d{3})-\d{3}\s+" # course and course number, skip the section number cuz we dont need dat
    r"(?P<A>\d+)\s+" # A grades
    r"(?P<B>\d+)\s+" # B grades
    r"(?P<C>\d+)\s+" # C grades
    r"(?P<D>\d+)\s+" # D grades
    r"(?P<F>\d+)\s+" # F grades
    r"(?P<total>\d+)\s+" # total students
    r"(?P<gpa>\d\.\d{3})\s+" # average GPA
    r"(?P<I>\d+)\s+" # incomplete; hours not included in GPA calculation
    r"(?P<S>\d+)\s+" # satisfactory; basically means class is pass/fail only
    r"(?P<U>\d+)\s+" # unsatisfactory; you didn't pass the class and it was a pass/fail class
    r"(?P<Q>\d+)\s+" # course dropped with no penalty, no grade points, hours not included in GPA calculation
    r"(?P<X>\d+)\s+" # no grade submitted, no grade points, hours not included in GPA calculation
    r"\d+\s+" # skip the repeated total student value 
    r"(?P<instructor>[A-Za-z.,\s]+)" # professor name
)

valid_departments = []

def extract_header_data(clean_data):

    match = header_pattern.search(clean_data)
        
    return {
        "semester": match.group("semester"),
        "year": int(match.group("year")),
        "college": match.group("college"),
        "department": match.group("department")
    }

def extract_gpa_data(pdf_path, scraper=None):
    
    """ 
    Extracts GPA data from a PDF file and returns a dictionary
    Args:
        pdf_path (str): Path to the PDF file
        year (int): Year of the data
        college (str): College of the data
    Returns: dict : Extracted data
    """

    with pdfplumber.open(pdf_path) as pdf:
        courses = []

        for page in pdf.pages:
            raw_data = page.extract_text(keep_blank_chars=False, layout=True)
            clean_data = re.sub(r"\s{2,}", " ", raw_data)

            header_data = extract_header_data(clean_data)

            for match in course_pattern.finditer(clean_data):
                if scraper:
                    professor = match.group("instructor").strip()
                    rating = scraper.get_rmp_rating(professor, header_data["department"])

                    try:
                        rating = float(rating)
                    except:
                        pass

                courses.append(
                    {
                        "course": match.group("course"),
                        "professor": match.group("instructor").strip(),
                        "rating": rating,
                        "gpa": float(match.group("gpa")),
                        "grades": {
                            "A": int(match.group("A")), "B": int(match.group("B")), "C": int(match.group("C")), "D": int(match.group("D")), "F": int(match.group("F")), 
                            "I": int(match.group("I")), "S": int(match.group("S")), "U": int(match.group("U")), "Q": int(match.group("Q")), "X": int(match.group("X"))
                            },
                        "total_students": int(match.group("total")),
                        "department": header_data["department"]
                    }
                )
    
    return {
        "semester": header_data["semester"],
        "year": header_data["year"],
        "college": header_data["college"],
        "courses": courses
    }



if __name__ == "__main__":
    rmpscraper = rmp_scraper.RMPScraper("1003", "Texas A&M University")
    data = extract_gpa_data("2024FAMAYS.pdf", rmpscraper)

    collection.insert_one(data)
    print("Data inserted successfully!")
    rmpscraper.driver.quit() 

    # with pdfplumber.open("2024FAENGR.pdf") as pdf:
    #     raw_data = pdf.pages[89].extract_text(keep_blank_chars=False, layout=True)
    #     clean_data = re.sub(r"\s{2,}", " ", raw_data)\
    #     header_data = extract_header_data(clean_data)

    #     print(repr(header_data))
        

# data = extract_gpa_data("2024FAENGR.pdf")
# collection.insert_one(data)
# print("Data inserted successfully!") 



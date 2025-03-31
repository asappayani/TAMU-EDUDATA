import modules.rmp_scraperv2 as rmp_scraper
import pdfplumber 
import re
from pprint import pp
from pymongo import MongoClient
import os
from typing import Collection, Optional, Dict

client = MongoClient("mongodb://localhost:27017/")
db = client["tamu_gpa"]
gpa_collection = db["gpa_distribution"]
ratings_collection = db["professor_ratings"]

HEADER_PATTERN = re.compile(
    r"FOR\s*(?P<semester>[A-Z]+)\s*(?P<year>\d{4})\s*.*?\s*" # semester and year
    r"COLLEGE:\s*(?P<college>[A-Z &,\/-]+(?: [A-Z&,\/-]+)*)\s+" # college or school name
    r"DEPARTMENT:\s*(?P<department>[A-Z &,\.\/-]+(?: [A-Z&,\.\/-]+)*)\s+TOTAL S", # department name
    re.DOTALL | re.IGNORECASE
)

COURSE_PATTERN = re.compile(
    r"(?P<course>[A-Z]+-\d{3})-\d{3}\s+"  # course code without section number
    r"(?P<A>\d+)\s+(?P<B>\d+)\s+(?P<C>\d+)\s+(?P<D>\d+)\s+(?P<F>\d+)\s+"  # grades A-F
    r"(?P<total>\d+)\s+(?P<gpa>\d\.\d{3})\s+"  # total students & GPA
    r"(?P<I>\d+)\s+(?P<S>\d+)\s+(?P<U>\d+)\s+"  # incomplete, satisfactory, unsatisfactory
    r"(?P<Q>\d+)\s+(?P<X>\d+)\s+\d+\s+"  # drops & no-grade cases (skipping repeated total)
    r"(?P<instructor>[A-Za-z.,\s'\-]+)"  # instructor's name
)

def parse_header_info(clean_data):
    match = HEADER_PATTERN.search(clean_data)
    return {
        "semester": match.group("semester"),
        "year": int(match.group("year")),
        "college": match.group("college"),
        "department": match.group("department")
    }

def extract_course_data(match: re.Match, department: str, scraper: Optional[object] = None, ratings_collection: Optional[Collection] = None) -> Dict:
    professor = match.group("instructor").strip()

    return {
        "course": match.group("course"),
        "professor": professor,
        "gpa": float(match.group("gpa")),
        "grades": {grade: int(match.group(grade)) for grade in ["A", "B", "C", "D", "F", "I", "S", "U", "Q", "X"]},
        "total_students": int(match.group("total")),
        "department": department
    }

# TESTING
# for filename in os.listdir("data/2024FALL"):
#     if filename.endswith(".pdf"):
#         with pdfplumber.open(f"data/2024FALL/{filename}") as pdf:
#             for page in pdf.pages:
#                 text = page.extract_text()
#                 clean_data = text.replace("\n", " ").replace("\r", " ").strip()
#                 header_data = extract_header_data(clean_data)
#                 department = header_data["department"]
                    
#                     # Check if the department is valid

#                 for match in COURSE_PATTERN.finditer(clean_data):
#                     course_data = parse_course_data(match, department, rmp_scraper, ratings_collection)
                    
#                     if course_data:
#                         print("Match found for course data in page: ", page.page_number, "for file:", filename)
#                         print(course_data)
#                     else:
#                         raise RuntimeError("No match found for course data in page: ", page.page_number, "for file:", filename)
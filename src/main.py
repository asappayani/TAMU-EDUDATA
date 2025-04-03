import modules.rmp_scraperv2 as rmp_scraper
import pdfplumber 
import re
from pprint import pp
from pymongo import MongoClient
import os
from typing import Dict, Collection, Union

CLIENT = MongoClient("mongodb://localhost:27017/")
DB = CLIENT["tamu_gpa"]
GPA_COLLETION = DB["gpa_distribution"]
RMP_RATINGS_COLLECTION = DB["professor_ratings"]

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


def format_course_data(match: re.Match, department: str) -> Dict:
    return {
        "course": match.group("course"),
        "professor": match.group("instructor").strip(),
        "gpa": float(match.group("gpa")),
        "grades": {grade: int(match.group(grade)) for grade in ["A", "B", "C", "D", "F", "I", "S", "U", "Q", "X"]},
        "total_students": int(match.group("total")),
        "department": department
    }


def fetch_professor_rating(professor_name: str, department: str, rmp_scraper: rmp_scraper, ratings_collection: Collection) -> Union[float, str]:

    # check if the professor's rating is already in the database
    existing_rating = ratings_collection.find_one({"professor": professor_name, "department": department})
    if existing_rating:
        return existing_rating.get("rating", "N/A")
    
    # fetch the rating from RateMyProfessor using the scraper, put it in the database
    rating = rmp_scraper.get_professor_rating(professor_name, department)
    ratings_collection.insert_one({
        "professor": professor_name,
        "department": department,
        "rating": rating
    })

    return rating
    

def extract_course_data(pdf_path: str, rmp_scraper: rmp_scraper, gpa_collection: Collection, rmp_rating_collection: Collection) -> None:
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # extract the needed data
            raw_data = page.extract_text()
            clean_data = re.sub(r"\s{2,}", " ", raw_data).strip()
            header_data = parse_header_info(clean_data)

            # check if the pdf we're on already exists in the database
            existing_document = gpa_collection.find_one({
                "semester": header_data["semester"],
                "year": header_data["year"],
                "department": header_data["department"]
            })

            if existing_document:
                document_id = existing_document["_id"]
            else: # insert a new document if it doesn't exist
                document_id = gpa_collection.insert_one({
                    "semester": header_data["semester"],
                    "year": header_data["year"],
                    "college": header_data["college"],
                    "courses": []
                }).inserted_id

            # add each course data to the database
            for match in COURSE_PATTERN.finditer(clean_data):
                course_data = format_course_data(match, header_data["department"])
                course_data["rating"] = fetch_professor_rating(course_data["professor"], header_data["department"], rmp_scraper, rmp_rating_collection)

                gpa_collection.update_one(
                    {"_id": document_id},
                    {"$addToSet": {"courses": course_data}}
                )


scraper = rmp_scraper.RMPScraper()

for semester in os.listdir("data"):
    for pdf in os.listdir(os.path.join("data", semester)):
        if pdf.endswith(".pdf"):
            pdf_path = os.path.join("data", semester, pdf)
            try:
                extract_course_data(
                    pdf_path,
                    scraper,
                    GPA_COLLETION,
                    RMP_RATINGS_COLLECTION
                )

                print(f"Data from {pdf} inserted successfully!")
            except Exception as e:
                print(f"Error processing {pdf}: {e}")




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
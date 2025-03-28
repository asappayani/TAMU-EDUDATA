import pdfplumber 
import re
from pprint import pp
from pymongo import MongoClient
import rmp_scraper
import os


client = MongoClient("mongodb://localhost:27017/")
db = client["tamu_gpa"]
gpa_collection = db["gpa_distribution"]
ratings_collection = db["professor_ratings"]

# header regex pattern
header_pattern = re.compile(
    r"FOR\s*(?P<semester>[A-Z]+)\s*(?P<year>\d{4})\s*.*?\s*"
    r"COLLEGE:\s*(?P<college>[A-Z &\/-]+(?: [A-Z&\/-]+)*)\s+"
    r"DEPARTMENT:\s*(?P<department>[A-Z &\/-]+(?: [A-Z&\/-]+)*)\s+TOTAL S",
    re.DOTALL | re.IGNORECASE
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
    r"(?P<instructor>[A-Za-z.,\s-]+)" # professor name
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

def get_professor_rating(professor, department, scraper=None, ratings_collection=None):
    """Fetches professor rating from MongoDB or scraper and handles errors."""
    
    # Check if the rating already exists in the MongoDB ratings collection
    if ratings_collection != None:
        existing_rating = ratings_collection.find_one({"professor": professor, "department": department})
        if existing_rating:
            return existing_rating.get("rating", "No Rating")

    # If not found, scrape the rating
    try:
        rating = scraper.get_rmp_rating(professor, department)
        rating = float(rating)  # Convert rating to float
    except (ValueError, TypeError):
        rating = "No Rating"  # Handle case where scraping fails or rating is not a number
    
    # Save the new rating to MongoDB for future use
    if ratings_collection != None:
        ratings_collection.insert_one({
            "professor": professor,
            "department": department,
            "rating": rating
        })
    
    return rating

def parse_course_data(match, department, scraper=None, ratings_collection=None):

    """Parses and returns course data from a regex match."""
    professor = match.group("instructor").strip()
    rating = get_professor_rating(professor, department, scraper, ratings_collection) if scraper else "Rating N/A"

    return {
        "course": match.group("course"),
        "professor": professor,
        "rating": rating,
        "gpa": float(match.group("gpa")),
        "grades": {
            grade: int(match.group(grade)) 
            for grade in ["A", "B", "C", "D", "F", "I", "S", "U", "Q", "X"]
        },
        "total_students": int(match.group("total")),
        "department": department
    }

def extract_gpa_data(pdf_path, scraper=None, db_collection=None, ratings_collection=None):
    """ 
    Extracts GPA data from a PDF file and adds it to MongoDB.
    
    Args:
        pdf_path (str): Path to the PDF file.
        scraper (optional): Scraper object to fetch professor ratings.
        db_collection (optional): MongoDB collection object where data will be stored.
    
    Returns:
        dict: Document ID of the inserted data in MongoDB.
    """
 # Initialize a document in MongoDB with empty courses array
    document_id = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            raw_data = page.extract_text(keep_blank_chars=False, layout=True)
            clean_data = re.sub(r"\s{2,}", " ", raw_data).strip()
            
            # Extract header data from the page (assuming it can change per page)
            header_data = extract_header_data(clean_data)
            
            # If this is the first page, insert the main document into MongoDB
            if document_id is None:
                document_id = db_collection.insert_one({
                    "semester": header_data["semester"],
                    "year": header_data["year"],
                    "college": header_data["college"],
                    "courses": []
                }).inserted_id  # Get the ID of the inserted document

            # Process the courses and update MongoDB
            for match in course_pattern.finditer(clean_data):
                course_data = parse_course_data(match, header_data["department"], scraper, ratings_collection)

                # Update the MongoDB document by appending each course
                db_collection.update_one(
                    {"_id": document_id},  # Use the same document ID
                    {"$push": {"courses": course_data}}  # Append to "courses" array
                )

rmpscraper = rmp_scraper.RMPScraper("1003", "Texas A&M University")

# with pdfplumber.open("2024FALL_AGRI.pdf") as pdf:
#     for page in pdf.pages:
#         raw_data = page.extract_text(keep_blank_chars=False, layout=True)
#         clean_data = re.sub(r"\s{2,}", " ", raw_data).strip()
#         print(repr(clean_data))

#         pp(extract_header_data(clean_data))

for folder in os.listdir("SEMESTERS"):
    for pdf_file in os.listdir(os.path.join("SEMESTERS", folder)):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join("SEMESTERS", folder, pdf_file)
            try:
                extract_gpa_data(
                    pdf_path,
                    scraper=rmpscraper,
                    db_collection=gpa_collection,
                    ratings_collection=ratings_collection
                )

                print(f"Data from {pdf_file} inserted successfully!")
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")




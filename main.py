import pdfplumber 
import re
from pprint import pp

# REGEX PATTERN
course_pattern = re.compile(
    r"(?P<course>[A-Z]+-\d{3}-\d{3})\s+" # course and number
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

with pdfplumber.open("grd20243EN.pdf") as pdf:
    courses = []
    
    for page in pdf.pages:
        raw_data = page.extract_text(keep_blank_chars=False, layout=True)
        clean_data = re.sub(r"\s{2,}", " ", raw_data)

        
        for match in course_pattern.finditer(clean_data):
            courses.append(
                {
                    "course": match.group("course"),
                    "professor": match.group("instructor").strip(),
                    "gpa": float(match.group("gpa")),
                    "grades": {
                        "A": int(match.group("A")),
                        "B": int(match.group("B")),
                        "C": int(match.group("C")),
                        "D": int(match.group("D")),
                        "F": int(match.group("F")),
                        "I": int(match.group("I")),
                        "S": int(match.group("S")),
                        "U": int(match.group("U")),
                        "Q": int(match.group("Q")),
                        "X": int(match.group("X")),
                    },
                    "total_students": int(match.group("total"))
                }
            )

pp(courses)


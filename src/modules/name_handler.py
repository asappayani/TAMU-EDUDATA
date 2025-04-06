from rapidfuzz import fuzz
from typing import Tuple, Union


def __dash_handler(name: str) -> str:
    """ Handles the dash in the professor name for RMP query. """
    return name.split('-')[0]


def __process_rmprofessor_name(name: str) -> tuple[str, str]:
    """ Process the RateMyProfessor name for comparison. """
    cleaned_name = name.lower().strip()
    name_parts = cleaned_name.split()

    first_initial = name_parts[0][0] # get the first initial
    last_name = ' '.join(name_parts[1:]) # get the last name

    return (first_initial, last_name)


def process_professor_name(name: str, query: bool = False) -> Union[str, Tuple[str, str]]:
    """ Process the professor name for comparison or query. """
    cleaned_name = name.lower().strip()

    if ' ' not in name: # case 4 check
        return (None, cleaned_name) if not query else __dash_handler(cleaned_name)
    
    name_parts = cleaned_name.split()
    first_initial = name_parts[-1][0] # get the first initial
    last_name = __dash_handler(' '.join(name_parts[:-1])) if query else ' '.join(name_parts[:-1])

    return f"{first_initial} {last_name}" if query else (first_initial, last_name)


def get_name_match_score(prof_name: str, rmp_name: str) -> float:
    """ Returns the rapidfuzz match score between the professor name and the RateMyProfessor name. """
    prof_first_initial, prof_last_name = process_professor_name(prof_name)
    rmprof_first_initial, rmprof_last_name = __process_rmprofessor_name(rmp_name)

    if prof_first_initial is None: # Case 4
        return fuzz.ratio(prof_last_name, rmprof_last_name)

    if prof_first_initial != rmprof_first_initial: # Case 1
        return 0.0
    
    if len(prof_last_name) != len(prof_last_name): # Case 2
        return fuzz.partial_ratio(prof_last_name, rmprof_last_name)
    
    # Case 3
    return fuzz.ratio(prof_last_name, rmprof_last_name)


def get_department_name_match_score(professor_department: str, rmprofessor_department: str) -> float:
    """ Returns the match score between the professor department and the RateMyProfessor department. """

    score = fuzz.ratio(professor_department.lower().strip(), rmprofessor_department.lower().strip())
    return score 

if __name__ == "__main__":
    # Test the functions
    print(process_professor_name("KATEHI-TSEREGOUNS", query=True)) # Expected: "K Tsergounis"
   
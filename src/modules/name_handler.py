import rapidfuzz as fuzz
from typing import Tuple, Union

def dash_handler(name: str) -> str:
    ''' Handles the dash in the professor name for RMP query '''
    return name.split('-')[0]

def process_professor_name(name: str, query: bool = False) -> Union[str, Tuple[str, str]]:
    ''' Process the professor name for comparison or query '''

    if ' ' not in name: # case 4 check
        return (None, name.lower().strip()) if not query else name.lower().strip()
    
    name_parts = name.split()
    first_initial = name_parts[-1][0] # get the first initial
    last_name = dash_handler(' '.join(name_parts[:-1])) if query else ' '.join(name_parts[:-1]) # handle the dash if query is True

    if query:
        return f"{first_initial} {last_name}".lower().strip() 
    else:
        return (
            first_initial.lower().strip(), 
            last_name.lower().strip()
        )

def process_rmprofessor_name(name: str) -> tuple[str, str]:
    ''' Process the RateMyProfessor name for comparison '''
    name_parts = name.split()
    first_initial = name_parts[0][0] # get the first initial
    last_name = ' '.join(name_parts[1:]) # get the last name

    return (
        first_initial.lower().strip(), 
        last_name.lower().strip()
    )

def get_name_match_score(prof_name: str, rmp_name: str) -> float:
    ''' Returns the match score between the professor name and the RateMyProfessor name '''
    prof_first_initial, prof_last_name = process_professor_name(prof_name)
    rmprof_first_initial, rmprof_last_name = process_rmprofessor_name(rmp_name)

    if prof_first_initial is None: # case 4
        return fuzz.ratio(prof_last_name, rmprof_last_name)

    if prof_first_initial != rmprof_first_initial: # case 1
        return 0.0
    
    if len(prof_last_name) < len(rmprof_last_name) or len(rmprof_last_name) < len(prof_last_name): # case 2
        return fuzz.partial_ratio(prof_last_name, rmprof_last_name)
    else: # case 3
        return fuzz.ratio(prof_last_name, rmprof_last_name)
    


def get_department_name_match_score(department: str, valid_departments: set) -> bool:
    """
    Cases:
    1. If the department is in the valid departments, return True
    2. If the department is not in the valid departments, return False
    3. If the department is not in the valid departments but is close to one of them, return True
    """
    pass

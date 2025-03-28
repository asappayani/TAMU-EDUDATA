import rapidfuzz as fuzz

def dash_handler(name: str) -> str:
    ''' Handles the dash in the professor name for RMP query '''
    return name.split('-')[0]

def process_professor_name(name: str, query: bool = False) -> str:
    ''' Process the professor name for comparison or query '''

    if ' ' not in name: # case 4 check
        return name.lower().strip()
    
    name_parts = name.split()
    first_initial = name_parts[-1][0] # get the first initial
    last_name = dash_handler(' '.join(name_parts[:-1])) if query else ' '.join(name_parts[:-1]) # handle the dash if query is True

    return f"{first_initial} {last_name}".lower().strip()

def process_rmprofessor_name(name: str) -> str:
    ''' Lower and strip the RMP professor name for comparison '''
    return name.lower().strip()

def get_name_match_score(prof_name: str, rmp_name: str) -> float:
    """
    Cases:
    1. First initial of prof name doesn't match first letter of rmp name, return 0.0
    2. Length of last name of prof is less than rmp or vice versa, then we need a partial ratio
    3. Length of last name of prof is equal to rmp, then we need a ratio
    4. If just the last name is passed, then we need to compare the last name with the rmp last name

    TODO: process the names, then follow the cases above, return the score
    """
    pass

def get_department_name_match_score(department: str, valid_departments: set) -> bool:
    """
    Cases:
    1. If the department is in the valid departments, return True
    2. If the department is not in the valid departments, return False
    3. If the department is not in the valid departments but is close to one of them, return True
    """
    pass

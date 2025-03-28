import rapidfuzz as fuzz

def dash_handler(name: str) -> str:
    # TODO: split the name by the dash and return the part before the dash
    pass

def process_professor_name(name: str, query: bool = False) -> str:
    """
    Cases: 
    1. Last name then first initial
    2. Last name with dash then first initial
    3. Last name with two words then first initial
    4. Just last name
    TODO: Put the first initial at the front, then put everything else after
    TODO: SPECIAL CASE: if the name is just the last name, return the last name
    
    SPECIAL CASE, query is true:
    everything should be same but,
    TODO: send the last name to dash handler so that the dash is removed and we return first initial with just the first part of last name before the dash
    """
    pass

def process_rmprofessor_name(name: str) -> str:
    # TODO: lower and strip the name and return it
    pass

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
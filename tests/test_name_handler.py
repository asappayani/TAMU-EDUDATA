from src.modules.name_handler import process_professor_name, dash_handler, get_name_match_score, get_department_name_match_score, process_rmprofessor_name
import pytest

# dash_handler 

# process_professor_name
"""
Cases: 
1. Last name then first initial
2. Last name with dash then first initial
3. Last name with two words then first initial
4. Just last name

Query Cases:
everything should be same but,
Send the last name to dash handler so that the dash is removed and we return first initial with just the first part of last name before the dash lower and stripped

SPECIAL CASE: if the name is just the last name, return the last name lower and stripped, should be returned regardless of the query case 
"""

# process_rmprofessor_name
"""
Should return the first initial and the last name, lower and stripped
"""

# get_name_match_score
"""
Cases:
1. First initial of prof name doesn't match first letter of rmp name, return 0.0
2. Length of last name of prof is less than rmp or vice versa, then we need a partial ratio
3. Length of last name of prof is equal to rmp, then we need a ratio
4. If just the last name is passed, then we need to compare the last name with the rmp last name
"""





import re

def camel_case_to_sentence_case(camel_case_str):
    # Use regular expression to insert a space before each capital letter
    sentence_case_str = re.sub(r'(?<!^)(?=[A-Z])', ' ', camel_case_str)
    # Capitalize the first letter of the result
    sentence_case_str = sentence_case_str[0].capitalize() + sentence_case_str[1:]
    return sentence_case_str
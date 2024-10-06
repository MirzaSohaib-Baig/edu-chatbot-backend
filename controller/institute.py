import requests
from nltk.corpus import stopwords
import re

stop_words = set(stopwords.words('english'))

def camel_case_to_sentence_case(camel_case_str):
    # Use regular expression to insert a space before each capital letter
    sentence_case_str = re.sub(r'(?<!^)(?=[A-Z])', ' ', camel_case_str)
    # Capitalize the first letter of the result
    sentence_case_str = sentence_case_str[0].capitalize() + sentence_case_str[1:]
    return sentence_case_str

def getSubject(text, subject_list):

    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    capitalize_words = [word.capitalize() for word in filtered_words]
    subject = [word for word in capitalize_words if word in subject_list]
    return subject

def get_top_institutes(number_of_universities):

    # URL to fetch data from
    url = "https://www.timeshighereducation.com/sites/default/files/the_data_rankings/world_university_rankings_2024_0__91239a4509dc50911f1949984e3fb8c5.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Fetching the data from the URL
    response = requests.get(url, headers=headers)
    response_json = response.json()

    # Assuming the structure of JSON has relevant information about universities
    top_institutes = []

    counter = 0

    # This is just an example and assumes the structure; adapt based on actual JSON structure
    for uni in response_json['data'][:number_of_universities]:
        counter += 1
        uni_name = uni['name']
        uni_rank = uni['rank']
        uni_score = uni['scores_overall']
        uni_location = uni['location']
        response_message = f"<strong>{counter}.{uni_name}:</strong> This University has a ranking of {uni_rank} and an overall score of {uni_score}. It is located in {uni_location}."
        top_institutes.append(response_message)

    # Prepare the response
    response_message = f"Here are the top {number_of_universities} universities:\n<br><br>" + "\n<br><br>".join(top_institutes)

    return response_message

def get_courses(institute_name):

    # URL to fetch data from
    url = "https://www.timeshighereducation.com/sites/default/files/the_data_rankings/world_university_rankings_2024_0__91239a4509dc50911f1949984e3fb8c5.json"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Fetching the data from the URL
    response = requests.get(url, headers=headers)
    response_json = response.json()

    # Searching for the specified institute by name
    for uni in response_json['data']:
        uni_name = uni['name']

        # Check if the university name matches the given institute name
        if institute_name.lower() in uni_name.lower():
            uni_subjects_offered = uni.get('subjects_offered', 'No subjects listed').strip().split(",")

            # Formatting subjects as a bullet point list
            subjects_formatted = "\n".join([f"<li style='margin-left: 20px;'>{subject.strip()}</li>" for subject in uni_subjects_offered])

            # Prepare response with university details
            response_message = (f"The courses offered by {uni_name} are as follows:<br><br>{subjects_formatted}")
            
            return response_message

    # If the university is not found
    return f"Sorry, we couldn't find any information about {institute_name}."

# institute_name = "karachi"
# result = get_courses(institute_name)
# print(result)
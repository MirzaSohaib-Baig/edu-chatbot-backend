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

def getAnswers(text, answer_list):

    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    cleaned_text = " ".join(filtered_words).lower()
    correct_answer = [answer for answer in answer_list if answer.lower() in cleaned_text.split()]
    return correct_answer

def get_top_institutes(number_of_universities):

    # URL to fetch data from
    url = "https://www.timeshighereducation.com/sites/default/files/the_data_rankings/asia_university_rankings_2024_0__244af00c6394ccbb3a654fe5e00385c9.json"
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
        uni_subjects_offered = uni['subjects_offered'].strip().split(",")
        # Creating a list of subjects offered, each preceded by a bullet point or dot
        subjects_formatted = "\n".join([f"<li style='margin-left: 20px;'>{subject.strip()}</li>" for subject in uni_subjects_offered])
        response_message = f"<strong>{counter}.{uni_name}:</strong> This University has a ranking of {uni_rank} and an overall score of {uni_score}. It is located in {uni_location}. And the courses it offers are as follows:<br><br>{subjects_formatted}"
        top_institutes.append(response_message)

    # Prepare the response
    response_message = f"Here are the top {number_of_universities} universities:\n<br><br>" + "\n<br><br>".join(top_institutes)

    return response_message
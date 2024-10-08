import requests
import pandas as pd

# URL to fetch data from
url = "https://www.timeshighereducation.com/sites/default/files/the_data_rankings/world_university_rankings_2024_0__91239a4509dc50911f1949984e3fb8c5.json"
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

# Fetching the data from the URL
response = requests.get(url, headers=headers)
response_json = response.json()

# Searching for the specified institute by name
universities = [uni['name'] for uni in response_json['data']]

df = pd.DataFrame(universities, columns=['University'])
df.to_csv('quiz_data/universities.csv', index=False)

print("CSV file created successfully!")
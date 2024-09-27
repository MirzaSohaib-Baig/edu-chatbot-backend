from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import pandas as pd
from show_result.show_debug import debug_issue
from fuzzywuzzy import process, fuzz

subject_df = pd.read_csv('quiz_data/questions.csv',sep=',', header=None, names=['Subject', 'Question', 'Answer', 'Explanation'])
#print(quiz_list.head(2))
print("Questions Actions ==", subject_df.head())

# Strip any extra whitespace from the CSV data
subject_df['Question'] = subject_df['Question'].str.strip()

# Debugging to check the questions loaded
debug_issue("Loaded questions from CSV:")
debug_issue(subject_df['Question'].head())

class ActionProvideSolution(Action):

    def name(self) -> Text:
        return "action_provide_solution"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the user's message (question) from the latest input
        # user_question = tracker.get_slot("question").strip().lower()
        user_question = tracker.latest_message["text"].strip().lower()
        debug_issue(f"User's question: {user_question}")

        # # Check if the user's question exists in the CSV (case-insensitive)
        # if user_question in subject_df['Question'].str.lower().values:
        #     # If a matching question is found, retrieve the answer and explanation
        #     matching_question = subject_df[subject_df['Question'].str.lower() == user_question]
        #     answer = matching_question.iloc[0]['Answer']
        #     explanation = matching_question.iloc[0]['Explanation']
        #     debug_issue(f"Answer: {answer}, Explanation: {explanation}")
            
        #     # Send the response back with the answer and explanation
        #     dispatcher.utter_message(text=f"{answer}.<br><br><strong>Explanation:</strong><br>{explanation}")
        # else:
        #     # If no matching question is found
        #     dispatcher.utter_message(text="Sorry, I couldn't find an answer to that question. Please try another question.")
        
        closest_match, score = process.extractOne(user_question, list(subject_df['Question']), scorer=fuzz.partial_ratio)

        if score >= 50:
            matching_question = subject_df[subject_df['Question'] == closest_match]
            debug_issue(f"Found closest matching question: {closest_match}")
            answer = matching_question.iloc[0]['Answer']
            explanation = matching_question.iloc[0]['Explanation']
            debug_issue(f"Answer: {answer}, Explanation: {explanation}")
            # Send the response back with the answer and explanation
            dispatcher.utter_message(text=f"{answer}.<br><br><strong>Explanation:</strong><br>{explanation}")
        else:
            # If no matching question is found
            dispatcher.utter_message(text="Sorry, I couldn't find an answer to that question. Please try another question.")
        
        return []

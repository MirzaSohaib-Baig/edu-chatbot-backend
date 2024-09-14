from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import pandas as pd
from show_result.show_debug import debug_issue
from controller.institute import getSubject

subject_df = pd.read_csv('quiz_data/quizes.csv',sep=',', header=None, names=['Subject', 'Question', 'Answer', 'Explanation'])
#print(quiz_list.head(2))
debug_issue(subject_df.head())
subject_list = list(subject_df['Subject'])

# Fetching a quiz from an external source
class ActionFetchQuiz(Action):

    def name(self) -> Text:
        return "action_fetch_quiz"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        latest_text = tracker.latest_message['text']
        debug_issue(f"latest_text: {latest_text}")

        # Extract subject from user's message
        extracted_subject = getSubject(latest_text, subject_list)
        debug_issue(f"extracted_subject: {extracted_subject}")

        subject = tracker.get_slot("course")
        debug_issue(f"quiz: {subject}")

        if extracted_subject and subject_df['Subject'].str.contains(extracted_subject[0]).any():
            subject = extracted_subject[0]
            debug_issue(f"Detected subject: {subject}.")
        else:
            dispatcher.utter_message(text="Sorry, I couldn't find any valid subject in your message. Please provide a valid subject.")
            return []

        # Fetch a random quiz question for the detected subject
        subject_questions = subject_df[subject_df['Subject'] == subject]
        question_row = subject_questions.sample(n=1).iloc[0]  # Pick a random question

        question = question_row['Question']
        correct_answer = question_row['Answer']

        dispatcher.utter_message(text=f"{question}")
        return [SlotSet("correct_answer", correct_answer)]

# Action to verify the user's answer based on the CSV file
class ActionVerifyAnswer(Action):

    def name(self) -> Text:
        return "action_verify_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # user_answer = tracker.latest_message['text']  # User's answer
        user_answer = tracker.latest_message["text"]  # User's answer
        debug_issue(f"user_answer: {user_answer}")
        correct_answer = tracker.get_slot('correct_answer')
        debug_issue(f"correct_answer: {correct_answer}")

        # Fetch the explanation from the CSV file
        # subject = tracker.get_slot("course")
        # subject_questions = subject_df[subject_df['Subject'] == subject]
        # question_row = subject_questions[subject_questions['Answer'] == correct_answer].iloc[0]
        # explanation = question_row['Explanation']

        # Check if the user's answer matches the correct answer
        if user_answer == correct_answer:
            dispatcher.utter_message(text="Correct!")
        else:
            # dispatcher.utter_message(text=f"Incorrect. The correct answer is {correct_answer}. <br><br><strong>Explanation:</strong><br><br>{explanation}")
            dispatcher.utter_message(text=f"Incorrect. The correct answer is {correct_answer}.")
        
        return [SlotSet("correct_answer", None)]

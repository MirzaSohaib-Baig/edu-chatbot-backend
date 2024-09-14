from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionAskQuestion(Action):

    def name(self) -> Text:
        return "action_ask_question"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="What question would you like help with?")
        return []

# A custom action to provide a solution to a math problem
class ActionProvideSolution(Action):

    def name(self) -> Text:
        return "action_provide_solution"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        question = tracker.get_slot("question")
        # Dummy solution logic; in practice, this could be an API call
        if "2 + 2" in question:
            solution = "4"
        else:
            solution = "Sorry, I don't know the answer to that."

        dispatcher.utter_message(text=f"The solution to your problem is: {solution}")
        return []

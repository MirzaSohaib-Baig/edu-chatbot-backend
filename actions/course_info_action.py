from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from controller.institute import get_courses
from show_result.show_debug import debug_issue

# Fetching a quiz from an external source
class ActionTopInstitutes(Action):

    def name(self) -> Text:
        return "action_provide_courses"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Dummy quiz; in practice, fetch from a database or an API
        courses = tracker.get_slot("university_name")
        debug_issue(courses)
        if courses is not None:
            list_of_courses = get_courses(courses)
            debug_issue(list_of_courses)
            dispatcher.utter_message(text=list_of_courses)
        else:
            dispatcher.utter_message(text="Provide a valid institute name.")
        return [SlotSet("university_name", None)]

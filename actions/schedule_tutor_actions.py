from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# Action to schedule a tutoring session
class ActionScheduleSession(Action):

    def name(self) -> Text:
        return "action_schedule_session"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        subject = tracker.get_slot("course")
        # Dummy scheduling logic; in practice, integrate with a scheduling API
        dispatcher.utter_message(text=f"Your tutoring session for {subject} has been scheduled!")
        return []

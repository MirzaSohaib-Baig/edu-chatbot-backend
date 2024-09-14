from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from controller.institute import get_top_institutes
from show_result.show_debug import debug_issue

# Fetching a quiz from an external source
class ActionTopInstitutes(Action):

    def name(self) -> Text:
        return "action_fetch_top_institutes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Dummy quiz; in practice, fetch from a database or an API
        top_institutes = tracker.get_slot("total_institutes")
        debug_issue(top_institutes)
        list_of_institutes = get_top_institutes(int(top_institutes))
        debug_issue(list_of_institutes)
        dispatcher.utter_message(text=list_of_institutes)
        return []

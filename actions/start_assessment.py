from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionStartAssessment(Action):
    def name(self) -> Text:
        return "action_start_assessment"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        lang = tracker.get_slot("user_language")
        if lang == "en":
            message = "I just want to see how you've been feeling lately."
        else:
            message = "Solo quiero ver cómo te has estado sintiendo últimamente."
        dispatcher.utter_message(text=message)
        return []

from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher


class ActionSetLanguage(Action):
    def name(self) -> Text:
        return "action_set_language"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        text = tracker.latest_message['text'].lower()
        if 'english' in text:
            return [SlotSet("language", "en")]
        elif 'spanish' in text or 'español' in text:
            return [SlotSet("language", "es")]
        else:
            dispatcher.utter_message(text="Please choose English or Spanish.")
            return [FollowupAction("action_set_language")]
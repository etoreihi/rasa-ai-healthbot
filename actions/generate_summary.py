from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from ..utils.content_loader import load_summary


class ActionGenerateSummary(Action):
    def name(self) -> Text:
        return "action_generate_summary"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        lang = tracker.get_slot("language")
        summary_template = load_summary(lang)
        # Format with slot values
        summary = summary_template.format(
            top_domains=tracker.get_slot("top_domains"),
            intrusion_score=tracker.get_slot("intrusion_score"),
            avoidance_score=tracker.get_slot("avoidance_score"),
            hyperarousal_score=tracker.get_slot("hyperarousal_score"),
        )
        dispatcher.utter_message(text=summary)
        return []
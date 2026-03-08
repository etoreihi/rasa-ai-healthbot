from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from utils.scoring import calculate_domain_score, get_top_domains


class ActionCalculateScores(Action):
    def name(self) -> Text:
        return "action_calculate_scores"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        intrusion_score = calculate_domain_score([
            tracker.get_slot(f"intrusion_{i}") or 0 for i in range(1, 6)
        ])
        avoidance_score = calculate_domain_score([
            tracker.get_slot(f"avoidance_{i}") or 0 for i in range(1, 3)
        ])
        hyperarousal_score = calculate_domain_score([
            tracker.get_slot(f"hyperarousal_{i}") or 0 for i in range(1, 7)
        ])
        scores = {
            "Intrusion": intrusion_score,
            "Avoidance": avoidance_score,
            "Hyperarousal": hyperarousal_score,
        }
        top_domains = get_top_domains(scores)
        return [
            SlotSet("intrusion_score", intrusion_score),
            SlotSet("avoidance_score", avoidance_score),
            SlotSet("hyperarousal_score", hyperarousal_score),
            SlotSet("top_domains", top_domains),
        ]
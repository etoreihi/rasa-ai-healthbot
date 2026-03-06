from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher

from ..utils.scoring import parse_score
from ..utils.content_loader import load_question_config


class ActionParseScore(Action):
    def name(self) -> Text:
        return "action_parse_score"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        current_question = tracker.get_slot("current_question")
        text_slot = f"{current_question}_text"
        text = tracker.get_slot(text_slot)
        config = load_question_config()
        max_rephrases = config['questions'][current_question]['max_rephrases']

        if text and ("don't know" in text.lower() or "not sure" in text.lower() or "no sé" in text.lower()):
            count = tracker.get_slot("rephrase_count") or 0
            count += 1
            if count < max_rephrases:
                return [SlotSet("rephrase_count", count), FollowupAction("action_ask_question")]
            else:
                return [SlotSet(current_question, 0), SlotSet("rephrase_count", 0)]
        else:
            score = parse_score(text or "")
            return [SlotSet(current_question, score), SlotSet("rephrase_count", 0)]
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from ..utils.content_loader import load_questions


class ActionAskQuestion(Action):
    def name(self) -> Text:
        return "action_ask_question"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        lang = tracker.get_slot("language")
        question_id = tracker.get_slot("current_question")
        count = tracker.get_slot("rephrase_count") or 0
        try:
            question_text = load_questions(lang, question_id, count)
            dispatcher.utter_message(text=question_text)
        except (KeyError, IndexError):
            # Fallback if variant not found
            dispatcher.utter_message(text=f"Please answer the question for {question_id}.")
        return [SlotSet("current_question", question_id)]
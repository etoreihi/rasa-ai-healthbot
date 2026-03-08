from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher

from utils.scoring import needs_followup, parse_score, is_uncertain
from utils.content_loader import load_question_config, load_questions


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
        lang = tracker.get_slot("user_language") or "en"
        count = tracker.get_slot("rephrase_count") or 0
        is_context_question = (current_question or "").startswith("context_")

        if text and is_uncertain(text) and not is_context_question:
            count += 1
            if count < max_rephrases:
                if lang == "es":
                    dispatcher.utter_message(text="No hay problema. Te lo pregunto de otra manera.")
                else:
                    dispatcher.utter_message(text="No problem. Let me ask that in a different way.")
                # Clear current input slot and re-ask current question with next variant.
                try:
                    rephrased = load_questions(lang, current_question, count)
                    dispatcher.utter_message(text=rephrased)
                except Exception:
                    pass
                return [
                    SlotSet(text_slot, None),
                    SlotSet("rephrase_count", count),
                    FollowupAction("action_listen"),
                ]
            else:
                if lang == "es":
                    dispatcher.utter_message(
                        text="Está bien si no quieres hablar de esto ahora. Pasemos a la siguiente pregunta."
                    )
                else:
                    dispatcher.utter_message(
                        text="That's okay if you don't want to go into this right now. We'll move to the next question."
                    )
                return [SlotSet(current_question, 1), SlotSet("rephrase_count", 0)]

        if text and needs_followup(text) and count == 0 and not is_context_question:
            if lang == "es":
                dispatcher.utter_message(text="Gracias. ¿Podrías contarme un poco más para entenderte mejor?")
            else:
                dispatcher.utter_message(text="Thanks. Could you share a bit more so I can understand better?")
            return [SlotSet(current_question, 1), SlotSet("rephrase_count", 1)]

        score = parse_score(text or "", current_question or "")
        if is_context_question:
            return [SlotSet("rephrase_count", 0)]
        return [SlotSet(current_question, score), SlotSet("rephrase_count", 0)]

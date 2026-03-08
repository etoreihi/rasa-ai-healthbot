from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from utils.content_loader import load_questions, load_question_config


class ActionAskQuestion(Action):
    def name(self) -> Text:
        return "action_ask_question"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        lang = tracker.get_slot("user_language")
        question_id = tracker.get_slot("current_question")
        count = tracker.get_slot("rephrase_count") or 0
        if lang not in {"en", "es"}:
            lang = "en"
        user_role = (tracker.get_slot("user_role") or "").strip()
        user_setting = (tracker.get_slot("user_setting") or "").strip()

        def previous_question_id(qid: Text) -> Text:
            ordered = list(load_question_config()["questions"].keys())
            try:
                idx = ordered.index(qid)
            except ValueError:
                return ""
            if idx == 0:
                return ""
            return ordered[idx - 1]

        def transition_from_previous() -> Text:
            prev_qid = previous_question_id(question_id)
            if not prev_qid or count > 0:
                return ""
            prev_text = (tracker.get_slot(f"{prev_qid}_text") or "").lower().strip()
            if not prev_text:
                return ""

            stress_markers = {"stressed", "overwhelmed", "anxious", "panic", "stress", "estres", "ansioso", "abrumado"}
            low_markers = {"no", "nope", "not really", "none", "never", "not that much", "nada", "nunca", "no mucho", "para nada"}
            high_markers = {"very", "a lot", "often", "constantly", "mucho", "muy", "bastante", "siempre"}

            if any(m in prev_text for m in stress_markers):
                return (
                    "That sounds really heavy."
                    if lang == "en"
                    else "Eso suena realmente pesado."
                )
            if any(m in prev_text for m in high_markers):
                return (
                    "That sounds intense."
                    if lang == "en"
                    else "Eso suena intenso."
                )
            if any(m in prev_text for m in low_markers):
                return (
                    "Got it."
                    if lang == "en"
                    else "Entiendo."
                )
            try:
                idx = list(load_question_config()["questions"].keys()).index(prev_qid)
            except ValueError:
                idx = 0
            neutral_en = ["Thanks for explaining.", "I appreciate your openness.", "Got you."]
            neutral_es = ["Gracias por explicarlo.", "Aprecio tu apertura.", "Te entiendo."]
            return (neutral_en[idx % len(neutral_en)] if lang == "en" else neutral_es[idx % len(neutral_es)])

        def contextual_prefix() -> Text:
            if count > 0:
                return ""
            # Only personalize assessment questions to avoid sounding repetitive in context collection.
            if not question_id or question_id.startswith("context_"):
                return ""
            if user_role:
                if lang == "en":
                    return f"Given what you've shared as a {user_role},"
                return f"Con lo que compartiste como {user_role},"
            if user_setting:
                if lang == "en":
                    return f"In your {user_setting} setting,"
                return f"En tu entorno de {user_setting},"
            return ""

        try:
            question_text = load_questions(lang, question_id, count)
            lead_in = transition_from_previous()
            context_lead = contextual_prefix()
            if lead_in and context_lead:
                question_text = f"{lead_in} {context_lead} {question_text}"
            elif lead_in:
                question_text = f"{lead_in} {question_text}"
            elif context_lead:
                question_text = f"{context_lead} {question_text}"
            dispatcher.utter_message(text=question_text)
        except (KeyError, IndexError):
            # Fallback if variant not found
            dispatcher.utter_message(text=f"Please answer the question for {question_id}.")
        return [SlotSet("current_question", question_id)]

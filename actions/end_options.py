from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import Restarted, SlotSet
from rasa_sdk.executor import CollectingDispatcher


class ActionAskEndOptions(Action):
    def name(self) -> Text:
        return "action_ask_end_options"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        lang = tracker.get_slot("user_language") or "en"
        if lang == "es":
            dispatcher.utter_message(
                text="Si quieres, escribe: `summary` para ver el resumen otra vez, `restart` para empezar de nuevo, o `end` para terminar."
            )
        else:
            dispatcher.utter_message(
                text="If you want, type: `summary` to see the summary again, `restart` to start over, or `end` to finish."
            )
        return []


class ActionHandleEndChoice(Action):
    def name(self) -> Text:
        return "action_handle_end_choice"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        lang = tracker.get_slot("user_language") or "en"
        choice = (tracker.get_slot("end_choice") or "").strip().lower()

        if choice in {"summary", "resumen"}:
            summary = tracker.get_slot("last_summary_text") or ""
            if summary:
                dispatcher.utter_message(text=summary)
            if lang == "es":
                dispatcher.utter_message(text="Escribe `restart` para empezar de nuevo o `end` para terminar.")
            else:
                dispatcher.utter_message(text="Type `restart` to start over or `end` to finish.")
            return [SlotSet("end_choice", None)]

        if choice in {"restart", "start", "again", "reiniciar", "empezar"}:
            if lang == "es":
                dispatcher.utter_message(text="Perfecto, empecemos de nuevo.")
            else:
                dispatcher.utter_message(text="Okay, let's start again.")
            return [Restarted()]

        # Default: end conversation politely
        if lang == "es":
            dispatcher.utter_message(
                text="Si estás pasando por un momento difícil, busca apoyo de un profesional de salud calificado. Cuídate."
            )
        else:
            dispatcher.utter_message(
                text="If you're experiencing distress, please reach out to a qualified healthcare provider. Take care."
            )
        return [SlotSet("end_choice", "end")]

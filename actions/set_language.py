from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
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
        raw = (tracker.get_slot("user_language") or tracker.latest_message.get("text") or "").strip()
        text = raw.lower()
        # Lightweight language detection from first user text.
        spanish_markers = {
            "hola",
            "buenos",
            "buenas",
            "gracias",
            "como",
            "cómo",
            "estoy",
            "quiero",
            "siento",
            "tengo",
            "me",
            "no sé",
            "no se",
            "español",
            "espanol",
        }

        if text in {"es", "spanish", "español", "espanol"} or "spanish" in text:
            return [SlotSet("user_language", "es")]
        if text in {"en", "english", "inglés", "ingles"} or "english" in text:
            return [SlotSet("user_language", "en")]
        if any(token in text for token in spanish_markers) or any(ch in text for ch in "áéíóúñ¿¡"):
            return [SlotSet("user_language", "es")]
        # Default to English for ambiguous short inputs like "hi".
        return [SlotSet("user_language", "en")]

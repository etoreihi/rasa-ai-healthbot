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
        lang = tracker.get_slot("language")
        if lang == "en":
            message = "Great! We'll proceed in English. This assessment will ask about symptoms related to intrusion, avoidance, and hyperarousal. Please answer on a scale from 0 to 4: 0 = Not at all, 1 = A little bit, 2 = Moderately, 3 = Quite a bit, 4 = Extremely. If you're not sure, just say 'I don't know'."
        else:
            message = "¡Genial! Procederemos en español. Esta evaluación preguntará sobre síntomas relacionados con intrusión, evitación e hiperactivación. Por favor, responde en una escala del 0 al 4: 0 = Nada, 1 = Un poco, 2 = Moderadamente, 3 = Bastante, 4 = Extremadamente. Si no estás seguro, di 'No sé'."
        dispatcher.utter_message(text=message)
        return []
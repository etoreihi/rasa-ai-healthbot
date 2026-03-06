from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionClosing(Action):
    def name(self) -> Text:
        return "action_closing"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        lang = tracker.get_slot("language")
        if lang == "en":
            message = "Thank you for participating in this assessment. Remember, this is not a substitute for professional medical advice. If you're experiencing distress, please reach out to a qualified healthcare provider. Take care!"
        else:
            message = "Gracias por participar en esta evaluación. Recuerde, esto no es un sustituto del consejo médico profesional. Si está experimentando angustia, por favor contacte a un proveedor de atención médica calificado. ¡Cuídese!"
        dispatcher.utter_message(text=message)
        return []
import re
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher


ROLE_KEYWORDS = {
    "nurse": ["nurse", "rn", "lpn", "np", "enfermera", "enfermero"],
    "physician": ["doctor", "physician", "md", "médico", "medico"],
    "therapist": ["therapist", "counselor", "psychologist", "terapeuta", "psicólogo", "psicologo"],
    "technician": ["tech", "technician", "paramedic", "emt", "técnico", "tecnico"],
    "administrative": ["admin", "manager", "coordinator", "office", "administrativo"],
}

SETTING_KEYWORDS = {
    "hospital": ["hospital", "er", "icu", "emergency", "urgencias"],
    "clinic": ["clinic", "outpatient", "ambulatory", "clínica", "clinica"],
    "long-term care": ["nursing home", "long term", "ltc", "residencia"],
    "community": ["community", "home health", "public health", "comunidad"],
}

SPANISH_MARKERS = {
    "hola",
    "gracias",
    "me he",
    "me siento",
    "estresado",
    "estresada",
    "enfermera",
    "enfermero",
    "años",
    "trabajo",
    "hospital",
    "clínica",
    "clinica",
}


def _detect_role(text: str) -> str:
    low = (text or "").lower()
    for role, keys in ROLE_KEYWORDS.items():
        for k in keys:
            # Single tokens use word boundaries; phrases use direct contains.
            if " " in k:
                if k in low:
                    return role
            else:
                if re.search(rf"\b{re.escape(k)}\b", low):
                    return role
    return ""


def _detect_setting(text: str) -> str:
    low = (text or "").lower()
    for setting, keys in SETTING_KEYWORDS.items():
        for k in keys:
            if " " in k:
                if k in low:
                    return setting
            else:
                if re.search(rf"\b{re.escape(k)}\b", low):
                    return setting
    return ""


def _detect_years(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"(\d{1,2})\s*(?:\+?\s*)?(?:years?|yrs?|años?)", text.lower())
    if m:
        return m.group(1)
    return ""


def _detect_language(text: str) -> str:
    low = (text or "").lower()
    if any(ch in low for ch in "áéíóúñ¿¡"):
        return "es"
    if any(marker in low for marker in SPANISH_MARKERS):
        return "es"
    return ""


class ActionExtractBackground(Action):
    def name(self) -> Text:
        return "action_extract_background"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        context_text = " ".join(
            [
                tracker.get_slot("context_1_text") or "",
                tracker.get_slot("context_2_text") or "",
                tracker.get_slot("context_3_text") or "",
                tracker.get_slot("context_4_text") or "",
            ]
        ).strip()

        lang = tracker.get_slot("user_language") or ""
        detected_lang = _detect_language(context_text)
        if detected_lang:
            lang = detected_lang

        role = tracker.get_slot("user_role") or _detect_role(context_text)
        setting = tracker.get_slot("user_setting") or _detect_setting(context_text)
        years = tracker.get_slot("user_experience_years") or _detect_years(context_text)

        return [
            SlotSet("user_language", lang),
            SlotSet("user_role", role),
            SlotSet("user_setting", setting),
            SlotSet("user_experience_years", years),
        ]

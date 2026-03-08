from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

class ActionGenerateSummary(Action):
    def name(self) -> Text:
        return "action_generate_summary"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        lang = tracker.get_slot("user_language")
        if lang not in {"en", "es"}:
            lang = "en"

        role = tracker.get_slot("user_role") or "healthcare professional"
        years = tracker.get_slot("user_experience_years") or "unspecified"
        setting = tracker.get_slot("user_setting") or "current setting"

        intrusion = [int(tracker.get_slot(f"intrusion_{i}") or 0) for i in range(1, 6)]
        avoidance = [int(tracker.get_slot(f"avoidance_{i}") or 0) for i in range(1, 3)]
        hyperarousal = [int(tracker.get_slot(f"hyperarousal_{i}") or 0) for i in range(1, 7)]

        intrusion_score = int(tracker.get_slot("intrusion_score") or 0)
        avoidance_score = int(tracker.get_slot("avoidance_score") or 0)
        hyperarousal_score = int(tracker.get_slot("hyperarousal_score") or 0)
        top_domains = tracker.get_slot("top_domains") or []

        item_labels = {
            "en": {
                "intrusion": ["sudden memories/images", "dreams", "reliving moments", "emotional waves", "physical distress from reminders"],
                "avoidance": ["avoiding thoughts/feelings", "avoiding people/situations"],
                "hyperarousal": ["always on guard", "easily startled", "concentration difficulty", "sleep disruption", "irritability/anger", "risk-taking behavior"],
            },
            "es": {
                "intrusion": ["recuerdos/imágenes repentinas", "sueños", "revivir momentos", "oleadas emocionales", "malestar físico por recordatorios"],
                "avoidance": ["evitar pensamientos/emociones", "evitar personas/situaciones"],
                "hyperarousal": ["estar siempre en guardia", "sobresalto fácil", "dificultad para concentrarse", "problemas de sueño", "irritabilidad/enojo", "conductas de riesgo"],
            },
        }

        def top_items(values: List[int], labels: List[str]) -> List[str]:
            indexed = sorted(enumerate(values), key=lambda x: x[1], reverse=True)
            chosen = [f"{labels[i]} ({v}/4)" for i, v in indexed[:2] if v >= 2]
            return chosen

        intr_top = top_items(intrusion, item_labels[lang]["intrusion"])
        av_top = top_items(avoidance, item_labels[lang]["avoidance"])
        hyp_top = top_items(hyperarousal, item_labels[lang]["hyperarousal"])

        if lang == "en":
            summary = (
                "For testing the chatbot purposes, here are the user's scores:\n"
                f"- Background: role={role}, years_experience={years}, setting={setting}\n"
                f"- Domain totals: Intrusion={intrusion_score}/20, Avoidance={avoidance_score}/8, Hyperarousal={hyperarousal_score}/24\n"
                f"- Top two domains: {top_domains}\n"
                f"- Intrusion item scores: {intrusion}\n"
                f"- Avoidance item scores: {avoidance}\n"
                f"- Hyperarousal item scores: {hyperarousal}\n\n"
                "Focused guidance based on higher-scored areas:\n"
                f"- Intrusion focus: {', '.join(intr_top) if intr_top else 'No strong intrusion hotspots identified.'}\n"
                f"- Avoidance focus: {', '.join(av_top) if av_top else 'No strong avoidance hotspots identified.'}\n"
                f"- Hyperarousal focus: {', '.join(hyp_top) if hyp_top else 'No strong hyperarousal hotspots identified.'}\n\n"
                "Practical next steps:\n"
                "- For high reactivity/startle or being on edge: use brief grounding (5-4-3-2-1) and paced breathing 2-3 times daily.\n"
                "- For concentration/sleep strain: set one short decompression routine after shifts and reduce stimulation 60 minutes before bed.\n"
                "- For lower-scored areas: keep protective habits (regular meals, hydration, movement, social support) to prevent escalation.\n"
                "- Track changes weekly so you can see which domain is improving and where support is still needed."
            )
        else:
            summary = (
                "Para fines de prueba del chatbot, aquí están las puntuaciones del usuario:\n"
                f"- Contexto: rol={role}, años_experiencia={years}, entorno={setting}\n"
                f"- Totales por dominio: Intrusión={intrusion_score}/20, Evasión={avoidance_score}/8, Hiperactivación={hyperarousal_score}/24\n"
                f"- Dos dominios principales: {top_domains}\n"
                f"- Puntuaciones de intrusión: {intrusion}\n"
                f"- Puntuaciones de evasión: {avoidance}\n"
                f"- Puntuaciones de hiperactivación: {hyperarousal}\n\n"
                "Guía enfocada según las áreas con mayor puntuación:\n"
                f"- Enfoque en intrusión: {', '.join(intr_top) if intr_top else 'No se identificaron focos altos de intrusión.'}\n"
                f"- Enfoque en evasión: {', '.join(av_top) if av_top else 'No se identificaron focos altos de evasión.'}\n"
                f"- Enfoque en hiperactivación: {', '.join(hyp_top) if hyp_top else 'No se identificaron focos altos de hiperactivación.'}\n\n"
                "Siguientes pasos prácticos:\n"
                "- Para sobresalto/alerta constante: usa grounding breve (5-4-3-2-1) y respiración pausada 2-3 veces al día.\n"
                "- Para concentración/sueño: implementa una rutina corta de descarga después del turno y baja estímulos 60 minutos antes de dormir.\n"
                "- Para áreas con puntajes bajos: mantén hábitos protectores (comidas regulares, hidratación, movimiento, apoyo social).\n"
                "- Revisa cambios semanalmente para ver qué dominio mejora y dónde aún necesitas apoyo."
            )

        dispatcher.utter_message(text=summary)
        return [SlotSet("last_summary_text", summary)]

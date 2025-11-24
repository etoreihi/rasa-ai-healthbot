import os
from typing import Any, Text, Dict, List, Optional, Tuple
from random import choice
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from openai import OpenAI

# ========= OpenAI (LLM) =========
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ========= CONTEXT QUESTIONS =========
CONTEXT_QUESTIONS = [
    "Could you share a bit about your role or experience?",
    "When you’re ready, could you walk me through what happened in your own words?",
    "How did you first realize the situation had occurred—or who brought it to your attention?",
    "What happened to the patient as a result, or what were you most concerned might happen?",
    "How did the team’s reactions or attitudes feel to you during and after the situation?",
    "How has this affected you—emotionally, physically, or at work—since it happened?"
]

# ========= IES-R conversational topics =========
INT_TOPICS = [
    "Do memories about what happened pop up on their own sometimes?",
    "Have thoughts about it made it hard to fall or stay asleep?",
    "Do things during the day bring it back to mind?",
    "Do you ever feel like you’re right back in the moment?",
    "Do images about it pop into your mind unexpectedly?",
    "Do reminders bring up strong feelings for you?",
    "Do waves of strong emotion come up about it?",
    "Have you had dreams about it recently?"
]

AVD_TOPICS = [
    "Do you try not to let yourself get upset when it comes up?",
    "Does any part of it feel unreal or distant?",
    "Do you avoid people, places, or things that remind you of it?",
    "Do you try not to think about it?",
    "Do you still have feelings about it but tend to avoid dealing with them?",
    "Do your feelings feel numb or muted when you think about it?",
    "Do you try to push the memory away?",
    "Do you prefer not to talk about it?"
]

HYP_TOPICS = [
    "Have you felt more irritable or easily angered lately?",
    "Do you feel jumpy or startle more easily than usual?",
    "Is it hard to fall asleep when you try to rest?",
    "Has it been tough to concentrate?",
    "When reminded of it, do you feel body reactions like a pounding heart or nausea?",
    "Do you feel on-guard or watchful much of the time?"
]

def get_queue(sub: Text):
    return {"intrusion": INT_TOPICS, "avoidance": AVD_TOPICS, "hyperarousal": HYP_TOPICS}.get(sub, [])

def next_phase(sub: Text):
    return {"intrusion": "avoidance", "avoidance": "hyperarousal"}.get(sub, "done")

# ========= Empathy banks =========
EMP_THANKS = ["Thanks for sharing that.", "I appreciate you opening up.", "I’m here with you."]
EMP_VALIDATING = ["That makes sense.", "That sounds really tough.", "You’re not alone in this."]
EMP_GENTLE = ["We can go at your pace.", "I’m listening.", "Thank you for putting that into words."]

def pick_tone():
    return f"{choice(EMP_THANKS)} {choice(EMP_VALIDATING)} {choice(EMP_GENTLE)}"

# ========= Severity scoring (silent) =========
def estimate_severity(text: Optional[Text]) -> int:
    if not text:
        return 1
    t = text.lower()
    if any(w in t for w in ["extremely", "every night", "all the time", "overwhelmed", "panic", "keeps happening"]):
        return 4
    if any(w in t for w in ["often", "frequently", "quite a bit", "most days", "really bad"]):
        return 3
    if any(w in t for w in ["sometimes", "some days", "comes and goes", "moderate"]):
        return 2
    if any(w in t for w in ["a little", "rarely", "not much", "once in a while"]):
        return 1
    return 1

# ========= Hybrid reflection + paraphrased question =========
def hybrid_reflect_and_ask(user_text: Text, next_question: Text) -> Text:
    tone_hint = pick_tone()
    prompt = f"""
You are a trauma-informed conversational coach. Write exactly 2 sentences:

1) Reflect back what the user just expressed in a natural, empathetic way. No advice, no judgment.

2) Ask ONE gentle follow-up question that paraphrases this question:
"{next_question}"

Rules:
- No quotes.
- No repeating previous greetings.
- Stay warm, concise, human.
- Max 45 words total.

User said: "{user_text}"
Tone hint: "{tone_hint}"
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return f"{tone_hint} {next_question}"

def key_for_phase(phase: Text, sub: Text, idx: int):
    return f"{phase}:{sub}:{idx}"

def advance_index(idx: int, queue_len: int):
    return (idx + 1 < queue_len, idx + 1)

# ========= Actions =========

class ActionStartAssessment(Action):
    def name(self):
        return "action_start_assessment"

    def run(self, dispatcher, tracker, domain):

        # Reset all slots
        events = [
            SlotSet("current_phase", "context"),
            SlotSet("context_index", 0.0),
            SlotSet("current_subscale", "intrusion"),
            SlotSet("question_index", 0.0),
            SlotSet("intrusion_sum", 0.0),
            SlotSet("avoidance_sum", 0.0),
            SlotSet("hyper_sum", 0.0),
            SlotSet("last_prompt_key", ""),
        ]

        # Option B — Supportive human greeting
        greeting = (
            "Hi, I’m really glad you’re here. I want to understand what’s been going on for you. "
            "When you’re ready, could you tell me a little about your role or experience?"
        )

        dispatcher.utter_message(text=greeting)

        # First context question
        key = key_for_phase("context", "none", 0)
        events.append(SlotSet("last_prompt_key", key))

        return events


class ActionHandleUserAndNext(Action):
    def name(self):
        return "action_handle_user_and_next"

    def run(self, dispatcher, tracker, domain):

        phase = tracker.get_slot("current_phase") or "context"
        user_text = tracker.latest_message.get("text", "")

        # Silent scoring
        last_intent = tracker.get_intent_of_latest_message()
        intr = float(tracker.get_slot("intrusion_sum") or 0)
        avd  = float(tracker.get_slot("avoidance_sum") or 0)
        hyp  = float(tracker.get_slot("hyper_sum") or 0)

        if phase == "iesr":
            sev = estimate_severity(user_text)
            if last_intent == "express_intrusion_symptoms":
                intr += sev
            elif last_intent == "express_avoidance_symptoms":
                avd += sev
            elif last_intent == "express_hyperarousal_symptoms":
                hyp += sev

        events = [
            SlotSet("intrusion_sum", intr),
            SlotSet("avoidance_sum", avd),
            SlotSet("hyper_sum", hyp),
        ]

        last_key = tracker.get_slot("last_prompt_key") or ""

        # ------- CONTEXT PHASE -------
        if phase == "context":
            idx = int(tracker.get_slot("context_index") or 0)

            has_more, next_idx = advance_index(idx, len(CONTEXT_QUESTIONS))
            if has_more:
                next_q = CONTEXT_QUESTIONS[next_idx]
                key = key_for_phase("context", "none", next_idx)

                if key != last_key:
                    combined = hybrid_reflect_and_ask(user_text, next_q)
                    dispatcher.utter_message(text=combined)
                    return events + [
                        SlotSet("context_index", float(next_idx)),
                        SlotSet("last_prompt_key", key)
                    ]
                return events

            # transition to IES-R start
            sub = "intrusion"
            first_q = get_queue(sub)[0]
            key = key_for_phase("iesr", sub, 0)

            combined = hybrid_reflect_and_ask(
                user_text,
                f"Thanks for sharing that. I’d like to check how this has been affecting you day to day. {first_q}"
            )
            dispatcher.utter_message(text=combined)
            return events + [
                SlotSet("current_phase", "iesr"),
                SlotSet("current_subscale", sub),
                SlotSet("question_index", 0.0),
                SlotSet("last_prompt_key", key),
            ]

        # ------- IES-R PHASE -------
        sub = tracker.get_slot("current_subscale") or "intrusion"
        idx = int(tracker.get_slot("question_index") or 0)
        queue = get_queue(sub)

        has_more, next_idx = advance_index(idx, len(queue))
        if has_more:
            next_q = queue[next_idx]
            key = key_for_phase("iesr", sub, next_idx)

            if key != last_key:
                combined = hybrid_reflect_and_ask(user_text, next_q)
                dispatcher.utter_message(text=combined)
                return events + [
                    SlotSet("question_index", float(next_idx)),
                    SlotSet("last_prompt_key", key),
                ]
            return events

        # move to next subscale
        nxt = next_phase(sub)
        if nxt != "done":
            first_q = get_queue(nxt)[0]
            key = key_for_phase("iesr", nxt, 0)

            combined = hybrid_reflect_and_ask(
                user_text,
                f"Thank you. A few more quick checks so I understand the whole picture. {first_q}"
            )
            dispatcher.utter_message(text=combined)
            return events + [
                SlotSet("current_subscale", nxt),
                SlotSet("question_index", 0.0),
                SlotSet("last_prompt_key", key),
            ]

        # Finished everything → summary
        return events + [{"event": "action", "name": "action_finalize_summary"}]


class ActionFinalizeSummary(Action):
    def name(self):
        return "action_finalize_summary"

    def run(self, dispatcher, tracker, domain):

        intr = float(tracker.get_slot("intrusion_sum") or 0) / 8.0
        avd  = float(tracker.get_slot("avoidance_sum") or 0) / 8.0
        hyp  = float(tracker.get_slot("hyper_sum") or 0) / 6.0

        # backend categorization
        def level(x):
            if x < 1: return "low"
            if x < 2: return "mild"
            if x < 3: return "moderate"
            return "high"

        intr_l = level(intr)
        avd_l  = level(avd)
        hyp_l  = level(hyp)

        # pick profile
        if intr_l in ["moderate", "high"] or hyp_l in ["moderate", "high"]:
            profile = "heavier"
        elif avd_l in ["moderate", "high"]:
            profile = "avoidant"
        elif "mild" in [intr_l, avd_l, hyp_l]:
            profile = "mild"
        else:
            profile = "light"

        # final human summary
        if profile == "heavier":
            final = (
                "Thank you for sharing all of this with me. It sounds like this experience has "
                "been really weighing on you — mentally and physically. The way these memories "
                "come back, and how your body reacts, shows just how stressful the situation was.\n\n"
                "You deserve support as you work through this. Grounding techniques or slow breathing "
                "can help in the moment, but talking with someone you trust — a clinician or peer — may help too.\n\n"
                "I’m here if you'd like to explore coping tools together."
            )

        elif profile == "avoidant":
            final = (
                "Thank you for walking through this with me. It sounds like you’ve been carrying a lot internally "
                "and working hard to keep things contained. Avoidance makes sense when something feels overwhelming.\n\n"
                "Gently approaching the feelings instead of pushing them away can sometimes soften their impact. "
                "We can explore that together if you'd like."
            )

        elif profile == "mild":
            final = (
                "Thank you for sharing everything with me. It sounds like this experience still comes up for you "
                "in very human ways — affecting your focus or energy at times.\n\n"
                "Small grounding moments, slow breathing, or giving yourself space to process can make a real difference.\n\n"
                "If you’d like, I can walk you through a few coping strategies."
            )

        else:
            final = (
                "Thank you for talking through all of this with me. It sounds like you’ve been affected, "
                "but you’re navigating things with insight and resilience.\n\n"
                "If anything starts to feel heavier, checking in with someone you trust can help. "
                "I’m here if you want to go over coping tools or grounding strategies."
            )

        dispatcher.utter_message(text=final)
        return []

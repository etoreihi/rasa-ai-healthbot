# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

import os
import httpx # Import the new HTTP client library
from typing import Any, Text, Dict, List, Optional, Tuple
from random import choice
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from openai import OpenAI

# -----------------
# Define the proxy URL here, if needed.
# Since you're on Railway, you might be pulling this from environment variables.
# Example: proxy_url = os.environ.get("HTTP_PROXY") 
# If you don't need a proxy, just set it to None:
proxy_url = None # <-- RECOMMENDED TO TRY THIS FIRST IF YOU DON'T HAVE A PROXY

# -----------------
# Initialize the client:
if proxy_url:
    # If a proxy is set, create a custom httpx client and pass it in
    custom_http_client = httpx.Client(proxies=proxy_url)
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        http_client=custom_http_client # Use the new parameter
    )
else:
    # If no proxy is set, initialize normally
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )
# ========= CONTEXT QUESTIONS (from your doc) =========
# Order matters: we’ll ask all 6 first, conversationally.
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

def get_queue(sub: Text) -> List[Text]:
    return {"intrusion": INT_TOPICS, "avoidance": AVD_TOPICS, "hyperarousal": HYP_TOPICS}.get(sub, [])

def next_phase(sub: Text) -> Text:
    return {"intrusion": "avoidance", "avoidance": "hyperarousal"}.get(sub, "done")

# ========= Empathy banks (mixed into LLM prompt as “tone hints”) =========
EMP_THANKS = ["Thanks for sharing that.", "I appreciate you opening up.", "I’m here with you."]
EMP_VALIDATING = ["That makes sense.", "That sounds really tough.", "You’re not alone in this."]
EMP_GENTLE = ["We can go at your pace.", "I’m listening.", "Thank you for putting that into words."]

def pick_tone() -> Text:
    return f"{choice(EMP_THANKS)} {choice(EMP_VALIDATING)} {choice(EMP_GENTLE)}"

# ========= Severity heuristic (silent) =========
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

# ========= LLM: generate HYBRID (reflect + 1 paraphrased question) =========
def hybrid_reflect_and_ask(user_text: Text, next_question: Text) -> Text:
    """
    Produces 1–2 sentences:
      • sentence 1: reflective + empathetic summary of user_text (no advice, no judgment)
      • sentence 2: a single, warm paraphrase of next_question
    No quotes, no bullet points, no repetition.
    """
    tone_hint = pick_tone()
    prompt = f"""
You are a trauma-informed conversational coach. Write exactly 2 sentences:

1) Reflect back what the user just expressed in a natural, empathetic way. No advice. No judgment. No “I understand that…”
   Keep it concise and human, as if you’re mirroring their feelings/meaning.

2) Ask ONE gentle follow-up question that paraphrases this exact question while keeping its meaning:
   "{next_question}"

Constraints:
- Do NOT include quotation marks.
- Do NOT repeat earlier prompts or greetings.
- Stay warm, concise, and human.
- Max 45 words across both sentences.

User said: "{user_text}"
Tone hint to weave in subtly: "{tone_hint}"
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        text = resp.choices[0].message.content.strip()
        return text
    except Exception:
        # graceful fallback
        return f"{tone_hint} {next_question}"

# ========= Keys & helpers =========
def key_for_phase(phase: Text, sub: Text, idx: int) -> Text:
    return f"{phase}:{sub}:{idx}"

def advance_index(idx: int, queue_len: int) -> Tuple[bool, int]:
    """Return (has_more, next_idx) within current queue."""
    return (idx + 1 < queue_len, idx + 1)

# ========= Actions =========

class ActionStartAssessment(Action):
    def name(self) -> Text:
        return "action_start_assessment"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        # Reset everything
        events: List[Dict[Text, Any]] = [
            SlotSet("current_phase", "context"),
            SlotSet("context_index", 0.0),
            SlotSet("current_subscale", "intrusion"),
            SlotSet("question_index", 0.0),
            SlotSet("intrusion_sum", 0.0),
            SlotSet("avoidance_sum", 0.0),
            SlotSet("hyper_sum", 0.0),
            SlotSet("last_prompt_key", ""),
        ]
        # Ask the first context question with hybrid style (reflect last user if any)
        user_text = tracker.latest_message.get("text", "") or "Thanks for saying hi."
        q = CONTEXT_QUESTIONS[0]
        combined = hybrid_reflect_and_ask(user_text, q)
        key = key_for_phase("context", "none", 0)
        events.append(SlotSet("last_prompt_key", key))
        dispatcher.utter_message(text=combined)
        return events


class ActionHandleUserAndNext(Action):
    def name(self) -> Text:
        return "action_handle_user_and_next"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        phase = (tracker.get_slot("current_phase") or "context").lower()
        # 1) Build reflection + ask exactly ONE next question.
        user_text = tracker.latest_message.get("text", "")

        # 2) Score silently if in IES-R
        last_intent = tracker.get_intent_of_latest_message()
        intr = float(tracker.get_slot("intrusion_sum") or 0.0)
        avd  = float(tracker.get_slot("avoidance_sum") or 0.0)
        hyp  = float(tracker.get_slot("hyper_sum") or 0.0)
        if phase == "iesr":
            sev = estimate_severity(user_text)
            if last_intent == "express_intrusion_symptoms":
                intr += sev
            elif last_intent == "express_avoidance_symptoms":
                avd += sev
            elif last_intent == "express_hyperarousal_symptoms":
                hyp += sev

        events: List[Dict[Text, Any]] = [
            SlotSet("intrusion_sum", intr),
            SlotSet("avoidance_sum", avd),
            SlotSet("hyper_sum", hyp),
        ]

        # 3) Figure next question based on phase + indices, and STOP duplicates.
        last_key = tracker.get_slot("last_prompt_key") or ""

        if phase == "context":
            idx = int(tracker.get_slot("context_index") or 0)
            q = CONTEXT_QUESTIONS[idx]
            # next within context
            has_more, next_idx = advance_index(idx, len(CONTEXT_QUESTIONS))
            if has_more:
                next_q = CONTEXT_QUESTIONS[next_idx]
                key = key_for_phase("context", "none", next_idx)
                if key != last_key:
                    combined = hybrid_reflect_and_ask(user_text, next_q)
                    dispatcher.utter_message(text=combined)
                    events += [SlotSet("context_index", float(next_idx)), SlotSet("last_prompt_key", key)]
                    return events
                # if same key somehow, just return without re-sending
                return events
            else:
                # transition to iesr → intrusion[0]
                sub = "intrusion"
                next_q = get_queue(sub)[0]
                key = key_for_phase("iesr", sub, 0)
                combined = hybrid_reflect_and_ask(
                    user_text,
                    f"Thanks for sharing that. I’d like to check how this has been affecting you day to day. {next_q}"
                )
                dispatcher.utter_message(text=combined)
                events += [
                    SlotSet("current_phase", "iesr"),
                    SlotSet("current_subscale", sub),
                    SlotSet("question_index", 0.0),
                    SlotSet("last_prompt_key", key),
                ]
                return events

        # phase == iesr
        sub = (tracker.get_slot("current_subscale") or "intrusion").lower()
        idx = int(tracker.get_slot("question_index") or 0)
        queue = get_queue(sub)
        # advance within subscale
        has_more, next_idx = advance_index(idx, len(queue))
        if has_more:
            next_q = queue[next_idx]
            key = key_for_phase("iesr", sub, next_idx)
            if key != last_key:
                combined = hybrid_reflect_and_ask(user_text, next_q)
                dispatcher.utter_message(text=combined)
                events += [SlotSet("question_index", float(next_idx)), SlotSet("last_prompt_key", key)]
                return events
            return events

        # move to next subscale or finalize
        nxt = next_phase(sub)
        if nxt != "done":
            first_q = get_queue(nxt)[0]
            key = key_for_phase("iesr", nxt, 0)
            combined = hybrid_reflect_and_ask(
                user_text,
                f"Thank you. A few more quick checks so I understand the whole picture. {first_q}"
            )
            dispatcher.utter_message(text=combined)
            events += [
                SlotSet("current_subscale", nxt),
                SlotSet("question_index", 0.0),
                SlotSet("last_prompt_key", key),
            ]
            return events

        # finished all → summary
        events += [{"event": "action", "name": "action_finalize_summary"}]
        return events


class ActionFinalizeSummary(Action):
    def name(self) -> Text:
        return "action_finalize_summary"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        def qlevel(m: float) -> Text:
            if m < 1.0: return "minimal"
            if m < 2.0: return "mild to moderate"
            if m < 3.0: return "moderate to marked"
            return "high"

        intr = float(tracker.get_slot("intrusion_sum") or 0.0) / 8.0
        avd  = float(tracker.get_slot("avoidance_sum") or 0.0) / 8.0
        hyp  = float(tracker.get_slot("hyper_sum") or 0.0) / 6.0

        summary = (
            "Thank you for walking through all of this with me.\n\n"
            f"• Thoughts & memories: {qlevel(intr)}.\n"
            f"• Pulling away/avoiding: {qlevel(avd)}.\n"
            f"• Body responses (sleep, startle, focus): {qlevel(hyp)}.\n\n"
            "What can help next:\n"
            "• Two minutes of slow breathing or a grounding check-in.\n"
            "• A small routine to support sleep and a brief daily movement.\n"
            "• If these reactions keep getting in the way, a quick chat with a counselor can really help.\n\n"
            "If you’d like, we can try a coping practice now, or I can share resources."
        )
        dispatcher.utter_message(text=summary)
        return []

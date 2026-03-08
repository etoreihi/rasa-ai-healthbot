import re
from typing import Dict, Iterable, List, Set


NOT_SURE_PATTERNS: Set[str] = {
    "not sure",
    "i don't know",
    "dont know",
    "idk",
    "no sé",
    "no se",
    "ni idea",
}

VAGUE_PATTERNS: Set[str] = {
    "ok",
    "fine",
    "good",
    "bad",
    "normal",
    "same",
    "meh",
    "bien",
    "mal",
    "normal",
    "igual",
}

DEFINITE_SHORT_RESPONSES: Set[str] = {
    "no",
    "nope",
    "not really",
    "never",
    "none",
    "not that much",
    "nah",
    "nada",
    "no mucho",
    "nunca",
    "para nada",
}

NEGATION_WORDS: Set[str] = {
    "no",
    "not",
    "never",
    "none",
    "nada",
    "ninguno",
    "ninguna",
    "nunca",
}

STRONG_MARKERS: Set[str] = {
    "always",
    "constantly",
    "every day",
    "all day",
    "cannot",
    "can't",
    "cant",
    "extremely",
    "severe",
    "panic",
    "siempre",
    "constantemente",
    "todos los días",
    "todo el día",
    "no puedo",
    "extremadamente",
    "grave",
    "pánico",
}

HIGH_MARKERS: Set[str] = {
    "often",
    "frequently",
    "very",
    "a lot",
    "quite a bit",
    "frecuente",
    "frecuentemente",
    "muy",
    "mucho",
    "bastante",
}

MILD_MARKERS: Set[str] = {
    "sometimes",
    "occasionally",
    "a little",
    "slightly",
    "some",
    "a bit",
    "a veces",
    "ocasionalmente",
    "un poco",
    "ligeramente",
    "algo",
}

# Topic words are language-agnostic enough for simple lexical scoring.
TOPIC_KEYWORDS: Dict[str, Set[str]] = {
    "intrusion": {
        "memory",
        "memories",
        "recuerdo",
        "recuerdos",
        "image",
        "images",
        "imagen",
        "imágenes",
        "dream",
        "dreams",
        "nightmare",
        "nightmares",
        "sueño",
        "sueños",
        "pesadilla",
        "pesadillas",
        "flashback",
        "flashbacks",
        "trigger",
        "triggers",
        "recordatorio",
        "recordatorios",
        "distress",
        "angustia",
    },
    "avoidance": {
        "avoid",
        "avoiding",
        "avoidance",
        "evitar",
        "evito",
        "evitación",
        "numb",
        "numbness",
        "entumecido",
        "entumecimiento",
        "distance",
        "distancing",
        "alejo",
        "alejar",
        "withdraw",
        "withdrawing",
        "aislar",
        "aislado",
        "talk",
        "hablar",
    },
    "hyperarousal": {
        "irritable",
        "irritability",
        "irritabilidad",
        "startled",
        "jumpy",
        "sobresalto",
        "nervioso",
        "sleep",
        "insomnia",
        "dormir",
        "insomnio",
        "concentrate",
        "concentration",
        "focus",
        "concentración",
        "concentrarme",
        "guard",
        "on guard",
        "hypervigilant",
        "hipervigilante",
        "heart",
        "sweat",
        "palpitaciones",
        "sudor",
    },
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower().strip())


def _contains_any(text: str, patterns: Iterable[str]) -> bool:
    return any(p in text for p in patterns)


def is_uncertain(text: str) -> bool:
    normalized = _normalize(text)
    return _contains_any(normalized, NOT_SURE_PATTERNS)


def needs_followup(text: str) -> bool:
    normalized = _normalize(text)
    if not normalized:
        return True
    if normalized in DEFINITE_SHORT_RESPONSES:
        return False
    if _contains_any(normalized, MILD_MARKERS) or _contains_any(normalized, HIGH_MARKERS) or _contains_any(normalized, STRONG_MARKERS):
        return False
    # Very short free-text answers are usually too vague for reliable scoring.
    words = normalized.split()
    if len(words) <= 2:
        return True
    return normalized in VAGUE_PATTERNS


def _domain_from_question_id(question_id: str) -> str:
    if question_id.startswith("intrusion_"):
        return "intrusion"
    if question_id.startswith("avoidance_"):
        return "avoidance"
    if question_id.startswith("hyperarousal_"):
        return "hyperarousal"
    return "context"


def parse_score(text: str, question_id: str = "") -> int:
    """Infer a backend-only score from free text on a 0-4 scale."""
    normalized = _normalize(text)
    if not normalized:
        return 0

    # Strong explicit absence -> 0
    if _contains_any(normalized, NEGATION_WORDS) and _contains_any(
        normalized,
        {"none", "nothing", "never", "ninguno", "ninguna", "nada", "nunca"},
    ):
        return 0

    level = 2  # neutral default for meaningful free text
    if _contains_any(normalized, MILD_MARKERS):
        level = max(level, 1)
    if _contains_any(normalized, HIGH_MARKERS):
        level = max(level, 3)
    if _contains_any(normalized, STRONG_MARKERS):
        level = 4

    domain = _domain_from_question_id(question_id)
    if domain in TOPIC_KEYWORDS and _contains_any(normalized, TOPIC_KEYWORDS[domain]):
        # If relevant symptom content is present, keep at least moderate.
        level = max(level, 2)
        # Escalate if intensifiers co-occur with topic content.
        if _contains_any(normalized, HIGH_MARKERS):
            level = max(level, 3)
        if _contains_any(normalized, STRONG_MARKERS):
            level = 4

    return max(0, min(4, level))


def calculate_domain_score(items: list) -> float:
    """Sum the scores for a domain."""
    return sum(items)


def get_top_domains(scores: dict) -> list:
    """Get top 2 domains by score."""
    sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [domain for domain, _ in sorted_domains[:2]]

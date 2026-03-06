def parse_score(text: str) -> int:
    """Parse user text input to a score 0-4."""
    text = text.lower().strip()
    if 'not at all' in text or 'nada' in text or '0' in text:
        return 0
    elif 'a little' in text or 'un poco' in text or '1' in text:
        return 1
    elif 'moderately' in text or 'moderadamente' in text or '2' in text:
        return 2
    elif 'quite a bit' in text or 'bastante' in text or '3' in text:
        return 3
    elif 'extremely' in text or 'extremadamente' in text or '4' in text:
        return 4
    else:
        return 0  # default


def calculate_domain_score(items: list) -> float:
    """Sum the scores for a domain."""
    return sum(items)


def get_top_domains(scores: dict) -> list:
    """Get top 2 domains by score."""
    sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [domain for domain, _ in sorted_domains[:2]]
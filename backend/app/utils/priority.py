"""
Rule-based priority suggestion.
NOT AI — deterministic keyword matching only.
"""

URGENT_KEYWORDS = [
    "stored goods", "today", "urgent", "dangerous", "danger",
    "stopping", "not working", "warning", "pressure", "emergency",
    "immediately", "asap", "cold-room", "cold room",
]

HIGH_KEYWORDS = [
    "follow-up", "follow up", "yesterday", "waiting", "pump",
    "overdue", "no visit", "no update",
]


def suggest_priority(message: str) -> dict:
    """
    Returns {"suggested": "urgent"|"high"|"normal", "reason": str}
    based on simple keyword rules.
    """
    lower = message.lower()

    for kw in URGENT_KEYWORDS:
        if kw in lower:
            return {
                "suggested": "urgent",
                "reason": f'Message contains "{kw}" — possible urgent situation.',
            }

    for kw in HIGH_KEYWORDS:
        if kw in lower:
            return {
                "suggested": "high",
                "reason": f'Message contains "{kw}" — possible high-priority follow-up.',
            }

    return {"suggested": "normal", "reason": "No urgent keywords detected."}

"""
Identifies requests that are missing important information.
These are deterministic heuristics, not AI.
"""

# Terms that indicate a specific, identifiable piece of equipment
SPECIFIC_EQUIPMENT = [
    "cold-room", "cold room", "pump", "compressor", "motor",
    "boiler", "chiller", "freezer", "hvac",
    "valve", "conveyor", "lift", "generator",
]

# Generic terms that refer to equipment but don't identify it
GENERIC_EQUIPMENT = ["machine", "unit", "equipment", "device", "system"]

# Vague symptoms that lack an equipment identifier
VAGUE_SYMPTOMS = ["not working", "broken down", "issue", "problem", "fault"]

# Terms implying a warning/alert that needs clarification about what exactly
WARNING_TERMS = ["warning", "alert", "alarm"]


def check_missing_info(message: str) -> list[str]:
    """
    Returns a list of missing information fields based on simple heuristics.
    """
    lower = message.lower()
    missing = []

    has_specific = any(kw in lower for kw in SPECIFIC_EQUIPMENT)
    has_generic = any(kw in lower for kw in GENERIC_EQUIPMENT)
    has_warning = any(kw in lower for kw in WARNING_TERMS)
    has_pressure = "pressure" in lower

    # Flag if only generic equipment mentioned without specific identifier
    if has_generic and not has_specific:
        missing.append("Equipment identifier missing")
    elif not has_generic and not has_specific:
        # No equipment mentioned at all
        missing.append("Equipment identifier missing")
    elif has_pressure and has_warning and not has_specific:
        # "pressure warning" without specific equipment
        missing.append("Equipment identifier missing")

    # Flag warnings/alerts that don't specify what is alarming
    if has_warning and not has_specific:
        if "Equipment identifier missing" not in missing:
            missing.append("Equipment identifier missing")

    # Flag very short / vague messages
    words = lower.split()
    skip_brief_check = any(kw in lower for kw in [
        "inspect", "routine", "check", "running", "thanks", "replacement",
    ])
    if len(words) < 6 and not skip_brief_check:
        missing.append("Problem description too brief")

    return missing

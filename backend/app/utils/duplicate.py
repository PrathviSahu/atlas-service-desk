"""
Simple duplicate detection — deterministic, no ML.
Checks same customer + keyword overlap.
"""

COLD_KEYWORDS = {"cold", "cold-room", "coldroom", "cold room", "freezer", "chiller"}
PUMP_KEYWORDS = {"pump"}
PRESSURE_KEYWORDS = {"pressure"}
GENERAL_KEYWORDS = {"not working", "broken", "fault", "fault", "error", "issue", "problem"}


def _keyword_set(text: str) -> set:
    lower = text.lower()
    found = set()
    for kw in (
        COLD_KEYWORDS | PUMP_KEYWORDS | PRESSURE_KEYWORDS | GENERAL_KEYWORDS
    ):
        if kw in lower:
            found.add(kw)
    return found


def find_duplicate_candidates(request: dict, all_requests: list[dict]) -> list[dict]:
    """
    Returns requests that are likely duplicates of `request`.
    A candidate must:
      1. Have the same customer_id
      2. Share at least one keyword
      3. Not already be the same request
      4. Not itself already marked as a duplicate
    """
    candidates = []
    req_keywords = _keyword_set(request["message"])

    for other in all_requests:
        if other["id"] == request["id"]:
            continue
        if other["customer_id"] != request["customer_id"]:
            continue
        if other["is_duplicate"]:
            continue
        other_keywords = _keyword_set(other["message"])
        shared = req_keywords & other_keywords
        if shared:
            candidates.append({
                "id": other["id"],
                "shared_keywords": list(shared),
                "customer_id": other["customer_id"],
                "message_snippet": other["message"][:80],
            })

    return candidates

"""Maps a free-text question to one of the predefined questions. No SQL is generated."""
import re
from difflib import SequenceMatcher

from questions import QUESTIONS, Question

STOP = {"the", "a", "an", "of", "is", "are", "what", "which", "how", "does", "do", "in", "by",
        "for", "to", "me", "show", "tell", "our", "we", "and", "on", "has", "have", "with", "it"}


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z\-]+", text.lower()) if t not in STOP}


def route(text: str, threshold: float = 0.2) -> Question | None:
    toks = _tokens(text)
    if not toks:
        return None
    best, best_score = None, 0.0
    for q in QUESTIONS:
        kw = set(q.keywords)
        overlap = len(toks & kw) / max(len(toks), 1)
        sim = SequenceMatcher(None, text.lower(), q.title.lower()).ratio()
        score = 0.7 * overlap + 0.3 * sim
        if score > best_score:
            best, best_score = q, score
    return best if best_score >= threshold else None

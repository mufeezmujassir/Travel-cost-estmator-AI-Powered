from typing import Optional, Dict, Any
from math import sqrt

from fastapi import Depends
from services.auth_service import get_current_user, get_optional_current_user


async def build_user_context(include: bool, current_user=Depends(get_optional_current_user)) -> Optional[Dict[str, Any]]:
    """Build a compact user context block for chatbot consumption.
    This function is designed to be called from a FastAPI route with DI, but can
    also be awaited manually by passing include=False to skip.
    """
    if not include:
        return None

    try:
        if not current_user:
            return None
        return {
            "user": {
                "name": getattr(current_user, "name", None),
                "email": getattr(current_user, "email", None),
                "type": getattr(current_user, "type", None),
                "subscriptionStatus": getattr(current_user, "subscriptionStatus", None),
                "generationsRemaining": getattr(current_user, "generationsRemaining", None),
            }
        }
    except Exception:
        return None


def cosine_similarity(a: Dict[str, int], b: Dict[str, int]) -> float:
    if not a or not b:
        return 0.0
    common = set(a.keys()) & set(b.keys())
    dot = sum(a[t] * b[t] for t in common)
    na = sqrt(sum(v * v for v in a.values()))
    nb = sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

def text_to_vec(s: str) -> Dict[str, int]:
    import re
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    tokens = [t for t in s.split() if t]
    vec: Dict[str, int] = {}
    for t in tokens:
        vec[t] = vec.get(t, 0) + 1
    return vec


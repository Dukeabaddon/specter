import re
from typing import Dict, Any, List

SUSPENSION_TRIGGER_KEYWORDS = [
    r"\bwalang\s+pasok\b",
    r"\bsuspendido\b",
    r"\bsuspended\b",
    r"\bsuspension\s+of\s+classes\b",
    r"\bclasses\s+are\s+suspended\b",
    r"\bklase\s+ay\s+suspendido\b",
    r"\bkanselado\b",
    r"\bcancelled\s+classes\b",
    r"\bno\s+classes\b",
]

LEVELS_PATTERNS = {
    "all_levels": r"\ball\s+levels\b|\blahat\s+ng\s+antas\b",
    "pre_school_to_shs": r"\b(pre[- ]school|kindergarten|elementarya|elementary|high\s*school|senior\s*high|k[- ]?12|basic\s+education)\b",
    "tertiary_college": r"\b(college|tertiary|unibersidad|pamantasan|graduate\s+school)\b",
    "public_private": r"\b(pampubliko\s+at\s+pribado|public\s+and\s+private)\b",
    "public_only": r"\b(public\s+schools?\s+only|pampubliko\s+lamang)\b",
}

REASON_PATTERNS = {
    "typhoon": r"\b(bagyo(ng)?|typhoon|tropical\s+(storm|depression)|signal\s+no\.?\s*\d+)\b",
    "monsoon_rain": r"\b(habagat|southwest\s+monsoon|heavy\s+rainfall|malakas\s+na\s+ulan|red\s+rainfall|orange\s+rainfall)\b",
    "flood": r"\b(baha(ng)?|flooding|pagbaha)\b",
    "heat_index": r"\b(heat\s+index|init|extreme\s+heat)\b",
    "strike_transport": r"\b(transport\s+strike|tigil[- ]pasada)\b",
}

class SuspensionClassifier:
    @staticmethod
    def classify(text: str) -> Dict[str, Any]:
        """
        Analyzes post text to determine if it is a class suspension notice.
        Returns a dict:
        {
            "is_suspension": bool,
            "confidence": float (0.0 to 1.0),
            "matched_triggers": List[str],
            "levels": List[str],
            "reasons": List[str],
        }
        """
        if not text:
            return {
                "is_suspension": False,
                "confidence": 0.0,
                "matched_triggers": [],
                "levels": [],
                "reasons": [],
            }

        text_lower = text.lower()
        matched_triggers = []
        for pat in SUSPENSION_TRIGGER_KEYWORDS:
            if re.search(pat, text_lower):
                matched_triggers.append(pat)

        matched_levels = []
        for level, pat in LEVELS_PATTERNS.items():
            if re.search(pat, text_lower):
                matched_levels.append(level)

        matched_reasons = []
        for reason, pat in REASON_PATTERNS.items():
            if re.search(pat, text_lower):
                matched_reasons.append(reason)

        is_suspension = len(matched_triggers) > 0
        
        # Calculate confidence
        confidence = 0.0
        if is_suspension:
            confidence = 0.6
            if matched_levels:
                confidence += 0.25
            if matched_reasons:
                confidence += 0.15
            confidence = min(1.0, confidence)

        return {
            "is_suspension": is_suspension,
            "confidence": round(confidence, 2),
            "matched_triggers": matched_triggers,
            "levels": matched_levels,
            "reasons": matched_reasons,
        }

import unicodedata
import re

def clean_unicode(text: str) -> str:
    if not text:
        return ""

    cleaned = []
    for ch in text:
        cat = unicodedata.category(ch)
        if cat.startswith("So") or cat.startswith("Cs"):
            continue
        cleaned.append(ch)

    text = "".join(cleaned)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\u200B-\u200F\uFEFF]", "", text)

    return text.strip()

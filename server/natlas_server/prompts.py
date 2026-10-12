"""Language-aware prompt helpers for N-ATLAS.

N-ATLAS supports English, Hausa (ha), Igbo (ig) and Yoruba (yo).
"""

LANGUAGES = {
    "en": "English",
    "ha": "Hausa",
    "ig": "Igbo",
    "yo": "Yoruba",
}

DEFAULT_SYSTEM_PROMPT = (
    "You are a large language model trained by Awarri AI technologies. "
    "You are a friendly assistant and you are here to help."
)

ATTRIBUTION = (
    "N-ATLaS is an initiative of the Federal Ministry of Communications, "
    "Innovation and Digital Economy, and powered by Awarri Technologies."
)


def language_name(code: str) -> str:
    code = (code or "").lower().strip()
    if code in LANGUAGES:
        return LANGUAGES[code]
    # Accept full names too ("hausa", "Yoruba")
    for k, v in LANGUAGES.items():
        if v.lower() == code:
            return v
    raise ValueError(
        f"Unsupported language '{code}'. Use one of: {', '.join(LANGUAGES)}"
    )


def reply_in_system_prompt(lang: str) -> str:
    name = language_name(lang)
    # Stating that it understands all four languages stops the model refusing
    # input in one language when asked to answer in another.
    return (
        f"{DEFAULT_SYSTEM_PROMPT} You understand English, Hausa, Igbo and Yoruba. "
        f"Always reply in {name}, whatever language the user writes in."
    )


def reply_in_reminder(lang: str, input_lang: str | None = None) -> str:
    # Appended to the latest user message: after a few English turns the model
    # follows the conversation and ignores the system prompt. Naming the input
    # language keeps it from answering "please write in English" instead.
    name = language_name(lang)
    if input_lang and language_name(input_lang) != name:
        return f"\n\n(This message is in {language_name(input_lang)}. Reply in {name}.)"
    return f"\n\n(Reply in {name}.)"


def translate_messages(text: str, source: str | None, target: str) -> list[dict]:
    tgt = language_name(target)
    src = f"from {language_name(source)} " if source else ""
    return [
        {
            "role": "system",
            "content": (
                "You are a professional Nigerian-language translator. "
                "Return ONLY the translation, with no explanation, notes or quotes."
            ),
        },
        {
            "role": "user",
            "content": f"Translate the following text {src}into {tgt}:\n\n{text}",
        },
    ]


# Lightweight, dependency-free language guess. Good enough to route prompts;
# not a replacement for a trained language-ID model.
_MARKERS = {
    "ha": ["ɗ", "ƙ", "ɓ", " da ", " ne ", " ce ", "menene", "yaya", "ina ", "kai ", "sannu", "na gode", " ba ", "wannan"],
    "ig": ["ị", "ụ", "ọ", "ṅ", " na ", " bụ ", "kedu", "nnọọ", "daalụ", " ka ", "unu", "anyị", " gị", "ndewo"],
    "yo": ["ẹ", "ọ", "ṣ", "à", "á", "è", "é", "ò", "ó", " ni ", " ti ", "bawo", "ẹ kú", "e ku", "jọwọ", "mo ", " wa ", "ṣe"],
}


def detect_language(text: str) -> dict:
    t = f" {text.lower()} "
    scores = {lang: sum(t.count(m) for m in marks) for lang, marks in _MARKERS.items()}
    # 'ọ' is shared by Igbo & Yoruba; Igbo-only dotted vowels break ties.
    if any(c in t for c in "ịụṅ"):
        scores["ig"] += 3
    if any(c in t for c in "ẹṣ"):
        scores["yo"] += 3
    if any(c in t for c in "ɗƙɓ"):
        scores["ha"] += 3
    best = max(scores, key=scores.get)
    total = sum(scores.values())
    if scores[best] == 0:
        return {"language": "en", "name": "English", "confidence": 0.5, "scores": scores}
    return {
        "language": best,
        "name": LANGUAGES[best],
        "confidence": round(scores[best] / total, 2),
        "scores": scores,
    }

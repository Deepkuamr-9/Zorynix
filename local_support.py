from __future__ import annotations

import re
from dataclasses import dataclass, field


CRISIS_PATTERNS = [
    r"\bkill myself\b",
    r"\bend my life\b",
    r"\bsuicid(?:e|al)\b",
    r"\bself[- ]harm\b",
    r"\bhurt myself\b",
    r"\bdon't want to live\b",
    r"\bwant to die\b",
    r"\bcan'?t go on\b",
]

INTENSIFIERS = {"very", "really", "so", "extremely", "completely", "totally"}

EMOTION_KEYWORDS = {
    "anxiety": {"anxious", "anxiety", "panic", "worried", "fear", "afraid", "nervous"},
    "sadness": {"sad", "down", "empty", "crying", "hurt", "hopeless", "low"},
    "anger": {"angry", "furious", "annoyed", "frustrated", "irritated", "mad"},
    "overwhelm": {"overwhelmed", "stressed", "burnt out", "burned out", "exhausted", "tired"},
    "loneliness": {"alone", "lonely", "isolated", "left out", "ignored"},
    "positive": {"good", "better", "happy", "grateful", "relieved", "hopeful", "calm", "great"},
}

TOPIC_KEYWORDS = {
    "work": {"work", "job", "boss", "office", "deadline", "career", "meeting", "manager"},
    "study": {"exam", "college", "school", "class", "study", "assignment", "marks", "semester"},
    "relationship": {"relationship", "partner", "boyfriend", "girlfriend", "breakup", "marriage"},
    "family": {"family", "mother", "mom", "father", "dad", "parents", "brother", "sister"},
    "friendship": {"friend", "friends", "best friend", "group", "roommate"},
    "sleep": {"sleep", "insomnia", "rest", "awake", "tired", "night"},
    "health": {"health", "therapy", "doctor", "medicine", "medication", "counselor"},
    "self_worth": {"useless", "worthless", "failure", "stupid", "not enough", "hate myself"},
}

GUIDANCE_PATTERNS = [
    "what should i do",
    "how do i",
    "can you help",
    "advice",
    "what can i do",
    "how can i",
]

GRATITUDE_PATTERNS = ["thanks", "thank you", "appreciate"]


@dataclass
class Analysis:
    is_crisis: bool
    intent: str
    primary_emotion: str
    secondary_emotion: str | None
    intensity: str
    topics: list[str] = field(default_factory=list)
    user_phrase: str = ""


def analyze_message(message: str) -> Analysis:
    text = normalize(message)
    is_crisis = any(re.search(pattern, text) for pattern in CRISIS_PATTERNS)

    topics = detect_topics(text)
    primary_emotion, secondary_emotion = detect_emotions(text)
    intent = detect_intent(text)
    intensity = detect_intensity(text, is_crisis)
    user_phrase = extract_reflective_phrase(message)

    return Analysis(
        is_crisis=is_crisis,
        intent=intent,
        primary_emotion=primary_emotion,
        secondary_emotion=secondary_emotion,
        intensity=intensity,
        topics=topics,
        user_phrase=user_phrase,
    )


def generate_support_response(message: str) -> str:
    analysis = analyze_message(message)

    if analysis.is_crisis:
        return crisis_response()

    parts = [
        build_opening(analysis),
        build_reflection(analysis),
        build_support_step(analysis),
        build_follow_up(analysis),
    ]
    return " ".join(part for part in parts if part)


def normalize(message: str) -> str:
    return re.sub(r"\s+", " ", message.lower()).strip()


def detect_topics(text: str) -> list[str]:
    topics: list[str] = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            topics.append(topic)
    return topics


def detect_emotions(text: str) -> tuple[str, str | None]:
    hits: list[tuple[str, int]] = []
    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score:
            hits.append((emotion, score))

    if not hits:
        return "mixed", None

    hits.sort(key=lambda item: item[1], reverse=True)
    primary = hits[0][0]
    secondary = hits[1][0] if len(hits) > 1 else None
    return primary, secondary


def detect_intent(text: str) -> str:
    if any(pattern in text for pattern in GRATITUDE_PATTERNS):
        return "gratitude"
    if "?" in text or any(pattern in text for pattern in GUIDANCE_PATTERNS):
        return "guidance"
    if any(phrase in text for phrase in ["i feel", "i am feeling", "i've been feeling", "i'm feeling"]):
        return "reflection"
    if any(word in text for word in ["today", "happened", "when", "after", "because"]):
        return "processing"
    return "sharing"


def detect_intensity(text: str, is_crisis: bool) -> str:
    if is_crisis:
        return "high"

    emphasis = text.count("!") + sum(text.count(word) for word in INTENSIFIERS)
    negative_density = sum(
        1
        for keywords in EMOTION_KEYWORDS.values()
        for keyword in keywords
        if keyword in text and keyword not in EMOTION_KEYWORDS["positive"]
    )

    if emphasis >= 2 or negative_density >= 4:
        return "high"
    if emphasis >= 1 or negative_density >= 2:
        return "medium"
    return "low"


def extract_reflective_phrase(message: str) -> str:
    cleaned = re.sub(r"\s+", " ", message.strip())
    if not cleaned:
        return ""

    sentence = re.split(r"(?<=[.!?])\s+", cleaned)[0]
    sentence = sentence.strip()
    if len(sentence) > 140:
        sentence = sentence[:137].rstrip() + "..."
    return sentence


def crisis_response() -> str:
    return (
        "I'm really glad you said this out loud. If you might act on these thoughts or you are not safe right now, "
        "please call your local emergency number immediately or go to the nearest emergency room. If possible, contact "
        "a trusted person right now and stay with them while you reach urgent human support."
    )


def build_opening(analysis: Analysis) -> str:
    if analysis.primary_emotion == "anxiety":
        return "That sounds tense and exhausting."
    if analysis.primary_emotion == "sadness":
        return "That sounds painful, and I'm glad you put it into words."
    if analysis.primary_emotion == "anger":
        return "It makes sense that you're feeling so frustrated."
    if analysis.primary_emotion == "overwhelm":
        return "It sounds like a lot has been piling up at once."
    if analysis.primary_emotion == "loneliness":
        return "That kind of loneliness can feel very heavy."
    if analysis.primary_emotion == "positive":
        return "I'm glad there's a little breathing room in what you're sharing."
    return "I'm here with you, and what you're describing matters."


def build_reflection(analysis: Analysis) -> str:
    topic_phrase = topic_reflection(analysis.topics)
    emotion_phrase = emotion_reflection(analysis)
    user_phrase = analysis.user_phrase

    if analysis.intent == "gratitude":
        return "You do not have to handle everything perfectly to be making progress."

    if user_phrase and analysis.intent in {"reflection", "processing"}:
        return f"You are carrying something real here: \"{user_phrase}\" {topic_phrase}{emotion_phrase}".strip()

    return f"{topic_phrase}{emotion_phrase}".strip() or "You do not need to solve all of it at once."


def topic_reflection(topics: list[str]) -> str:
    if "work" in topics:
        return "Work pressure can drain more than just your time. "
    if "study" in topics:
        return "Academic pressure can make even small things feel bigger. "
    if "relationship" in topics:
        return "Relationship stress can shake your sense of stability. "
    if "family" in topics:
        return "Family stress often hits deeply because it is so personal. "
    if "friendship" in topics:
        return "Feeling disconnected from friends can cut hard. "
    if "sleep" in topics:
        return "When sleep is off, everything else can feel sharper. "
    if "self_worth" in topics:
        return "When self-worth takes a hit, the mind can become much harsher than the truth. "
    return ""


def emotion_reflection(analysis: Analysis) -> str:
    if analysis.primary_emotion == "anxiety":
        return "It sounds like your mind is staying on high alert."
    if analysis.primary_emotion == "sadness":
        return "That sounds like more hurt than you should have to hold alone."
    if analysis.primary_emotion == "anger":
        return "There is a lot of pressure underneath that frustration."
    if analysis.primary_emotion == "overwhelm":
        return "Your system sounds overloaded rather than weak."
    if analysis.primary_emotion == "loneliness":
        return "Feeling unseen for too long can wear a person down."
    if analysis.primary_emotion == "positive":
        return "It sounds like some part of you can finally breathe."
    return ""


def build_support_step(analysis: Analysis) -> str:
    if analysis.intent == "guidance":
        return guidance_step(analysis)
    if "sleep" in analysis.topics:
        return "For tonight, try making the next 20 minutes quieter and simpler: dim the lights, put the phone away for a bit, and let your body slow down before expecting your mind to."
    if "work" in analysis.topics or "study" in analysis.topics:
        return "A gentle next move could be to write down the one task or problem that matters most right now and ignore the rest for the next 10 minutes."
    if "relationship" in analysis.topics or "family" in analysis.topics or "friendship" in analysis.topics:
        return "Before deciding what to say or do next, give yourself a pause long enough to separate your feelings from the other person's behavior."
    if analysis.primary_emotion in {"anxiety", "overwhelm"}:
        return "Try loosening your jaw, dropping your shoulders, and taking five slow breaths. Calming the body first can make the next decision feel less impossible."
    if analysis.primary_emotion in {"sadness", "loneliness"}:
        return "One kind next step could be reaching out to one trusted person or writing down the single thought that feels heaviest right now."
    if analysis.primary_emotion == "anger":
        return "If you can, give yourself a short gap before reacting. Even ten calmer minutes can protect you from saying something your stressed mind wants but your steadier self does not."
    return "We can take this one piece at a time instead of trying to fix the whole picture at once."


def guidance_step(analysis: Analysis) -> str:
    if "work" in analysis.topics:
        return "Start by separating what is urgent, what only feels urgent, and what can wait until tomorrow. That alone can lower the pressure."
    if "study" in analysis.topics:
        return "Try reducing the problem to one study block, one topic, or one question instead of the whole syllabus or whole exam."
    if "relationship" in analysis.topics or "family" in analysis.topics:
        return "A useful first step is deciding whether you need comfort, clarity, or a boundary, because those lead to very different conversations."
    if "self_worth" in analysis.topics:
        return "When the inner voice is harsh, start by questioning the conclusion, not fighting the feeling. Feelings can be real without being final."
    return "A good first step is to name the main problem in one short sentence, then choose the smallest action you can do in the next ten minutes."


def build_follow_up(analysis: Analysis) -> str:
    if analysis.intent == "gratitude":
        return "If you want, tell me what feels a little different for you right now."
    if analysis.intent == "guidance":
        return "If you want, tell me the part that feels most stuck and we can break it down further."
    if analysis.intensity == "high":
        return "If it helps, stay with just the next few minutes instead of the whole day."
    if analysis.secondary_emotion:
        return f"I can also hear some {analysis.secondary_emotion.replace('_', ' ')} underneath this."
    return "If you want, keep going and tell me which part feels hardest right now."

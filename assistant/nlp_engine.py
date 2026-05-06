"""
MAZE — Natural Language Processing Engine
Uses spaCy for intent classification, entity extraction, and sentiment analysis.
Falls back to keyword matching if spaCy is not available.
"""

import re
import os
import json

# ── Try to load spaCy ────────────────────────────────
_spacy_available = False
_nlp = None

def _init_spacy():
    """Initialize spaCy NLP pipeline."""
    global _spacy_available, _nlp
    try:
        import spacy
        # Try loading English model (small is fine for our use case)
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("   ⚠️  spaCy model not found. Downloading en_core_web_sm...")
            import subprocess, sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            _nlp = spacy.load("en_core_web_sm")
        _spacy_available = True
        return True
    except ImportError:
        print("   ⚠️  spaCy not installed. NLP features limited. Run: pip install spacy")
        return False
    except Exception as e:
        print(f"   ⚠️  spaCy init error: {e}")
        return False

_init_spacy()


# ── Intent Classification ────────────────────────────
# Maps common phrases/patterns to intents
INTENT_PATTERNS = {
    "greeting": {
        "keywords": ["hello", "hi", "hey", "howdy", "hola", "namaste", "good morning",
                     "good afternoon", "good evening", "good night", "what's up", "sup"],
        "patterns": [r"\b(hi|hey|hello|yo|hola)\b"]
    },
    "farewell": {
        "keywords": ["bye", "goodbye", "exit", "quit", "shutdown", "see you",
                     "good night", "take care", "later"],
        "patterns": [r"\b(bye|goodbye|exit|quit|shutdown)\b"]
    },
    "play_music": {
        "keywords": ["play", "song", "music", "youtube", "listen to", "put on"],
        "patterns": [r"\bplay\s+.+", r"\bput\s+on\s+.+", r"\blisten\s+to\s+.+"]
    },
    "open_app": {
        "keywords": ["open", "launch", "start", "run"],
        "patterns": [r"\b(open|launch|start|run)\s+\w+"]
    },
    "search": {
        "keywords": ["search", "google", "look up", "find", "wikipedia"],
        "patterns": [r"\b(search|google|find|look\s+up)\s+.+"]
    },
    "set_volume": {
        "keywords": ["volume", "louder", "quieter", "mute", "unmute", "sound"],
        "patterns": [r"\bvolume\s+(up|down|\d+)", r"\b(louder|quieter|mute)\b"]
    },
    "set_brightness": {
        "keywords": ["brightness", "brighter", "dimmer", "dim", "screen"],
        "patterns": [r"\bbrightness\s+(up|down|\d+)", r"\b(brighter|dimmer|dim)\b"]
    },
    "add_task": {
        "keywords": ["add task", "new task", "create task", "remind me", "reminder"],
        "patterns": [r"\b(add|create|new)\s+task\b", r"\bremind\s+me\b"]
    },
    "show_tasks": {
        "keywords": ["show task", "my task", "list task", "pending task", "tasks"],
        "patterns": [r"\b(show|list|view|my)\s+task"]
    },
    "take_note": {
        "keywords": ["note", "write down", "remember this", "jot down", "save note"],
        "patterns": [r"\b(note|write)\s+down\b", r"\bremember\s+this\b"]
    },
    "calculate": {
        "keywords": ["calculate", "math", "solve", "what is", "how much"],
        "patterns": [r"\bcalculate\b", r"\d+\s*[\+\-\*\/x×]\s*\d+"]
    },
    "weather": {
        "keywords": ["weather", "temperature", "forecast", "how hot", "how cold"],
        "patterns": [r"\bweather\s+in\s+\w+", r"\btemperature\s+in\s+\w+"]
    },
    "write_code": {
        "keywords": ["write code", "create code", "generate code", "code for",
                     "write program", "write script", "make code"],
        "patterns": [r"\b(write|create|generate|make)\s+(code|program|script)\b"]
    },
    "media_control": {
        "keywords": ["next", "previous", "skip", "pause", "resume", "stop"],
        "patterns": [r"\b(next|previous|skip|pause|resume|stop)\s*(track|song|music|video)?"]
    },
    "send_message": {
        "keywords": ["send message", "message", "whatsapp", "instagram", "text", "dm", "send a message"],
        "patterns": [r"\b(send\s+message|message|dm|text|whatsapp)\b"]
    },
    "call_person": {
        "keywords": ["call", "phone", "dial"],
        "patterns": [r"\bcall\b"]
    },
    "identity": {
        "keywords": ["who are you", "your name", "what are you", "introduce yourself"],
        "patterns": [r"\bwho\s+(are\s+you|r\s+u)\b", r"\byour\s+name\b"]
    },
    "help": {
        "keywords": ["help", "what can you do", "features", "capabilities"],
        "patterns": [r"\b(help|features|capabilities)\b"]
    },
    "motivation": {
        "keywords": ["motivate", "motivation", "inspire", "lazy", "feeling down",
                     "push me", "encourage"],
        "patterns": [r"\b(motivat|inspir|encourage)\w*\b"]
    },
    "joke": {
        "keywords": ["joke", "funny", "laugh", "humor", "make me laugh"],
        "patterns": [r"\bjoke\b", r"\bmake\s+me\s+laugh\b"]
    },
    "time_date": {
        "keywords": ["time", "date", "what time", "today", "day", "clock"],
        "patterns": [r"\bwhat\s+time\b", r"\btoday'?s?\s+date\b", r"\bwhat\s+day\b"]
    },
    "chat": {
        "keywords": [],  # Fallback intent
        "patterns": []
    }
}


class NLPResult:
    """Result of NLP analysis on user input."""
    def __init__(self):
        self.intent = "chat"           # Primary intent
        self.confidence = 0.0          # 0.0 to 1.0
        self.entities = {}             # Extracted entities {type: value}
        self.sentiment = "neutral"     # positive, negative, neutral
        self.sentiment_score = 0.0     # -1.0 to 1.0
        self.tokens = []               # Tokenized words
        self.noun_phrases = []         # Extracted noun phrases
        self.verbs = []                # Extracted verbs
        self.raw_text = ""             # Original text
        self.cleaned_text = ""         # Cleaned/normalized text

    def __repr__(self):
        return (f"NLPResult(intent='{self.intent}', confidence={self.confidence:.2f}, "
                f"sentiment='{self.sentiment}', entities={self.entities})")


def _classify_intent_keywords(text: str) -> tuple:
    """Keyword-based intent classification (fallback when spaCy unavailable)."""
    text_lower = text.lower().strip()
    best_intent = "chat"
    best_score = 0.0

    for intent, data in INTENT_PATTERNS.items():
        if intent == "chat":
            continue

        score = 0.0
        # Check keywords
        keyword_matches = sum(1 for kw in data["keywords"] if kw in text_lower)
        if keyword_matches > 0:
            score += keyword_matches * 0.3

        # Check regex patterns
        for pattern in data.get("patterns", []):
            if re.search(pattern, text_lower):
                score += 0.5
                break

        if score > best_score:
            best_score = score
            best_intent = intent

    # Normalize confidence to 0-1 range
    confidence = min(1.0, best_score)
    return best_intent, confidence


def _analyze_sentiment_basic(text: str) -> tuple:
    """Basic sentiment analysis without spaCy."""
    positive_words = {"good", "great", "amazing", "awesome", "love", "like", "happy",
                      "wonderful", "excellent", "fantastic", "nice", "cool", "best",
                      "perfect", "thank", "thanks", "beautiful", "brilliant"}
    negative_words = {"bad", "terrible", "hate", "awful", "worst", "stupid", "ugly",
                      "boring", "annoying", "frustrating", "sad", "angry", "disappointed",
                      "confused", "tired", "lazy", "can't", "don't", "never", "wrong"}

    words = set(text.lower().split())
    pos_count = len(words & positive_words)
    neg_count = len(words & negative_words)
    total = pos_count + neg_count

    if total == 0:
        return "neutral", 0.0
    
    score = (pos_count - neg_count) / total
    if score > 0.2:
        return "positive", score
    elif score < -0.2:
        return "negative", score
    return "neutral", score


def _extract_entities_basic(text: str) -> dict:
    """Basic entity extraction without spaCy."""
    entities = {}
    
    # Time patterns
    time_match = re.search(r'\b(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)?)\b', text, re.I)
    if time_match:
        entities["TIME"] = time_match.group(1)
    
    # Number patterns
    numbers = re.findall(r'\b(\d+(?:\.\d+)?)\b', text)
    if numbers:
        entities["NUMBER"] = numbers
    
    # App names
    app_names = ["notepad", "calculator", "chrome", "brave", "firefox", "edge",
                 "vscode", "vs code", "paint", "explorer", "terminal", "powershell",
                 "word", "excel", "powerpoint", "outlook", "telegram", "discord"]
    for app in app_names:
        if app in text.lower():
            entities["APP"] = app
            break
    
    # Website names
    websites = ["github", "gmail", "youtube", "google", "instagram", "twitter",
                "linkedin", "facebook", "reddit", "spotify", "netflix", "whatsapp"]
    for site in websites:
        if site in text.lower():
            entities["WEBSITE"] = site
            break
    
    return entities


def analyze(text: str) -> NLPResult:
    """Full NLP analysis of user input. Uses spaCy if available, falls back to basic."""
    result = NLPResult()
    result.raw_text = text
    result.cleaned_text = text.lower().strip()

    if _spacy_available and _nlp:
        return _analyze_with_spacy(text, result)
    else:
        return _analyze_basic(text, result)


def _analyze_with_spacy(text: str, result: NLPResult) -> NLPResult:
    """Full NLP analysis using spaCy."""
    doc = _nlp(text)

    # Tokenization
    result.tokens = [token.text for token in doc if not token.is_space]
    
    # Lemmatized tokens (base forms of words)
    lemmas = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]

    # Named Entity Recognition
    for ent in doc.ents:
        result.entities[ent.label_] = ent.text
    
    # Also extract basic entities (apps, websites, etc.)
    basic_entities = _extract_entities_basic(text)
    result.entities.update(basic_entities)

    # Noun phrases
    result.noun_phrases = [chunk.text for chunk in doc.noun_chunks]

    # Verbs
    result.verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]

    # Intent classification — use spaCy analysis + keyword matching
    # spaCy helps with understanding structure, keywords handle domain-specific intents
    result.intent, result.confidence = _classify_intent_spacy(doc, text)

    # Sentiment analysis
    result.sentiment, result.sentiment_score = _analyze_sentiment_spacy(doc, text)

    return result


def _classify_intent_spacy(doc, text: str) -> tuple:
    """Intent classification using spaCy + keyword matching."""
    text_lower = text.lower().strip()
    
    # Get verbs and objects for better understanding
    verbs = [token.lemma_.lower() for token in doc if token.pos_ == "VERB"]
    nouns = [token.lemma_.lower() for token in doc if token.pos_ in ("NOUN", "PROPN")]
    
    best_intent = "chat"
    best_score = 0.0

    for intent, data in INTENT_PATTERNS.items():
        if intent == "chat":
            continue

        score = 0.0
        
        # Keyword matching
        keyword_matches = sum(1 for kw in data["keywords"] if kw in text_lower)
        if keyword_matches > 0:
            score += keyword_matches * 0.25
        
        # Regex pattern matching
        for pattern in data.get("patterns", []):
            if re.search(pattern, text_lower):
                score += 0.4
                break
        
        # Verb-based boost (spaCy advantage)
        intent_verbs = {
            "play_music": ["play", "listen", "put"],
            "open_app": ["open", "launch", "start", "run"],
            "search": ["search", "find", "look", "google"],
            "add_task": ["add", "create", "remind", "remember"],
            "take_note": ["note", "write", "jot", "remember", "save"],
            "calculate": ["calculate", "solve", "compute"],
            "write_code": ["write", "create", "generate", "code", "build"],
            "set_volume": ["increase", "decrease", "raise", "lower", "set", "turn"],
            "set_brightness": ["increase", "decrease", "raise", "lower", "set", "turn"],
            "send_message": ["send", "message", "text", "dm"],
            "call_person": ["call", "dial", "phone"],
        }
        if intent in intent_verbs:
            verb_matches = sum(1 for v in verbs if v in intent_verbs[intent])
            score += verb_matches * 0.2
        
        # Noun-based boost
        intent_nouns = {
            "play_music": ["song", "music", "track", "video"],
            "set_volume": ["volume", "sound"],
            "set_brightness": ["brightness", "screen"],
            "add_task": ["task", "reminder"],
            "take_note": ["note", "message"],
            "calculate": ["math", "calculation"],
            "weather": ["weather", "temperature", "forecast"],
        }
        if intent in intent_nouns:
            noun_matches = sum(1 for n in nouns if n in intent_nouns[intent])
            score += noun_matches * 0.2

        if score > best_score:
            best_score = score
            best_intent = intent

    confidence = min(1.0, best_score)
    
    # If confidence is very low, default to chat
    if confidence < 0.2:
        best_intent = "chat"
    
    return best_intent, confidence


def _analyze_sentiment_spacy(doc, text: str) -> tuple:
    """Sentiment analysis using spaCy + lexicon."""
    # spaCy doesn't have built-in sentiment — use our lexicon approach
    # but enhanced with spaCy's understanding of negation
    
    positive_words = {"good", "great", "amazing", "awesome", "love", "like", "happy",
                      "wonderful", "excellent", "fantastic", "nice", "cool", "best",
                      "perfect", "thank", "thanks", "beautiful", "brilliant", "excited"}
    negative_words = {"bad", "terrible", "hate", "awful", "worst", "stupid", "ugly",
                      "boring", "annoying", "frustrating", "sad", "angry", "disappointed",
                      "confused", "tired", "lazy", "wrong", "fail", "suck"}
    
    pos_score = 0
    neg_score = 0
    
    for token in doc:
        word = token.lemma_.lower()
        
        # Check for negation (spaCy advantage!)
        is_negated = False
        for child in token.children:
            if child.dep_ == "neg":
                is_negated = True
                break
        
        if word in positive_words:
            if is_negated:
                neg_score += 1
            else:
                pos_score += 1
        elif word in negative_words:
            if is_negated:
                pos_score += 1
            else:
                neg_score += 1
    
    total = pos_score + neg_score
    if total == 0:
        return "neutral", 0.0
    
    score = (pos_score - neg_score) / total
    if score > 0.2:
        return "positive", score
    elif score < -0.2:
        return "negative", score
    return "neutral", score


def _analyze_basic(text: str, result: NLPResult) -> NLPResult:
    """Basic NLP analysis without spaCy."""
    # Simple tokenization
    result.tokens = text.split()
    
    # Basic entity extraction
    result.entities = _extract_entities_basic(text)
    
    # Keyword-based intent classification
    result.intent, result.confidence = _classify_intent_keywords(text)
    
    # Basic sentiment
    result.sentiment, result.sentiment_score = _analyze_sentiment_basic(text)
    
    return result


def extract_query(text: str, intent: str) -> str:
    """Extract the main query/subject from text based on intent.
    E.g., 'play some chill music on youtube' → 'chill music'
    """
    text_lower = text.lower().strip()
    
    # Words to strip based on intent
    strip_words = {
        "play_music": {"play", "some", "on", "youtube", "the", "a", "music", "song",
                       "please", "for", "me", "put", "listen", "to"},
        "open_app": {"open", "launch", "start", "run", "the", "a", "please", "for", "me"},
        "search": {"search", "google", "look", "up", "find", "for", "about", "the", "a",
                   "please", "me", "show"},
        "add_task": {"add", "task", "new", "create", "remind", "me", "to", "please", "a"},
        "take_note": {"note", "down", "write", "jot", "save", "remember", "this", "that",
                      "please", "a"},
        "weather": {"weather", "in", "the", "what", "is", "how", "forecast", "for",
                    "temperature"},
        "write_code": {"write", "create", "generate", "make", "code", "program", "script",
                       "for", "me", "a", "please", "that"},
        "send_message": {"send", "message", "to", "on", "whatsapp", "instagram", "text", "dm"},
        "call_person": {"call", "phone", "on", "whatsapp", "instagram"},
    }
    
    words_to_remove = strip_words.get(intent, set())
    if not words_to_remove:
        return text_lower
    
    words = text_lower.split()
    filtered = [w for w in words if w not in words_to_remove]
    return " ".join(filtered).strip()


def get_emotion_from_sentiment(sentiment: str, sentiment_score: float) -> str:
    """Map NLP sentiment to a voice emotion for edge-tts."""
    if sentiment == "positive":
        if sentiment_score > 0.6:
            return "excited"
        return "happy"
    elif sentiment == "negative":
        if sentiment_score < -0.6:
            return "sad"
        return "calm"
    return "calm"


def is_available() -> bool:
    """Check if NLP engine (spaCy) is available."""
    return _spacy_available

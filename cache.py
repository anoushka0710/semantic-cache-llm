import json
import os
import re
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_SIMILARITY_THRESHOLD = 0.55
STOPWORDS = {
    "a",
    "about",
    "an",
    "are",
    "by",
    "can",
    "do",
    "does",
    "explain",
    "for",
    "give",
    "how",
    "in",
    "is",
    "it",
    "me",
    "meant",
    "of",
    "please",
    "tell",
    "the",
    "to",
    "what",
    "when",
    "where",
    "who",
    "why",
    "with",
}

ABBREVIATIONS = {
    "ai": "artificial intelligence",
    "api": "application programming interface",
    "dsa": "data structures and algorithms",
    "gpt": "generative pretrained transformer",
    "llm": "large language model",
    "ml": "machine learning",
    "nlp": "natural language processing",
    "qa": "question answering",
    "rag": "retrieval augmented generation",
}

_CACHE_READY = False
_CACHE: List[Dict[str, Any]] = []

_CACHE_FILE = Path(__file__).with_name("gptcache_data") / "semantic_cache.json"


def normalize_query(query: str) -> str:
    text = query.lower().strip()
    text = text.replace("what's", "what is")
    text = text.replace("whats", "what is")
    text = re.sub(r"\bwhats\b", "what is", text)
    text = re.sub(r"[?!.:,;()\[\]{}]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _expand_abbreviations(text: str) -> str:
    expanded = text
    for acronym, phrase in ABBREVIATIONS.items():
        expanded = re.sub(rf"\b{re.escape(acronym)}\b", phrase, expanded)
    return expanded


def query_tokens(query: str) -> List[str]:
    text = _expand_abbreviations(normalize_query(query))
    tokens = re.findall(r"[a-z0-9]+", text)
    return [token for token in tokens if token not in STOPWORDS]


def semantic_similarity(left: str, right: str) -> float:
    left_tokens = query_tokens(left)
    right_tokens = query_tokens(right)

    if not left_tokens or not right_tokens:
        return 0.0

    left_set = set(left_tokens)
    right_set = set(right_tokens)

    overlap = len(left_set & right_set)
    union = len(left_set | right_set)
    token_score = overlap / union if union else 0.0

    left_text = " ".join(left_tokens)
    right_text = " ".join(right_tokens)
    sequence_score = SequenceMatcher(None, left_text, right_text).ratio()

    return round((0.65 * token_score) + (0.35 * sequence_score), 4)


def init_cache() -> None:
    global _CACHE_READY, _CACHE

    if _CACHE_READY:
        return

    if _CACHE_FILE.exists():
        try:
            _CACHE = json.loads(_CACHE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            _CACHE = []
    else:
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _CACHE = []

    _CACHE_READY = True


def _persist_cache() -> None:
    _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_FILE.write_text(json.dumps(_CACHE, indent=2), encoding="utf-8")


def set_similarity_threshold(threshold: float) -> None:
    global DEFAULT_SIMILARITY_THRESHOLD
    DEFAULT_SIMILARITY_THRESHOLD = max(0.0, min(1.0, float(threshold)))


def clear_cache() -> None:
    global _CACHE

    init_cache()
    _CACHE = []
    _persist_cache()


def get_cached_response(query: str, threshold: Optional[float] = None):
    init_cache()

    similarity_threshold = (
        DEFAULT_SIMILARITY_THRESHOLD if threshold is None else max(0.0, min(1.0, float(threshold)))
    )

    best_match = None
    best_score = 0.0

    for item in _CACHE:
        score = semantic_similarity(query, item["query"])
        if score > best_score:
            best_score = score
            best_match = item

    if best_match and best_score >= similarity_threshold:
        return best_match["response"]

    return None


def save_cached_response(query: str, response: str) -> None:
    init_cache()

    normalized_query = normalize_query(query)
    tokens = query_tokens(query)

    for item in _CACHE:
        if item["normalized_query"] == normalized_query:
            item["query"] = query
            item["tokens"] = tokens
            item["response"] = response
            _persist_cache()
            return

    _CACHE.append(
        {
            "query": query,
            "normalized_query": normalized_query,
            "tokens": tokens,
            "response": response,
        }
    )
    _persist_cache()

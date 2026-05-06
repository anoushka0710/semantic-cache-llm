import os
import re
import json
import pickle

from gptcache import Config, cache
from gptcache.adapter.api import get, put
from gptcache.embedding.string import to_embeddings
from gptcache.manager import manager_factory
from gptcache.processor.pre import get_prompt
from gptcache.similarity_evaluation import ExactMatchEvaluation


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
_SIMILARITY_THRESHOLD = 0.55
_LOCAL_CACHE = {}
_CACHE_FILE = os.path.join(os.path.dirname(__file__), "gptcache_data", "cache_store.pkl")


def normalize_query(query: str) -> str:
    text = query.lower().strip()
    text = text.replace("what's", "what is")
    text = text.replace("whats", "what is")
    text = re.sub(r"\bwhat\s+does\s+(.+?)\s+mean\b", r"what is \1", text)
    text = re.sub(r"\bwhat\s+do\s+(.+?)\s+mean\b", r"what is \1", text)
    text = re.sub(r"\bwhat\s+is\s+meant\s+by\b", "what is", text)
    text = re.sub(r"\bwhat\s+is\s+the\s+meaning\s+of\b", "what is", text)
    text = re.sub(r"\bexplain\b", "what is", text)
    text = re.sub(r"\bdefine\b", "what is", text)
    text = re.sub(r"\btell\s+me\s+about\b", "what is", text)
    # Remove articles
    text = re.sub(r"\s+\b(a|an|the)\b\s+", " ", text)
    text = re.sub(r"[?!.:,;]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _load_cache():
    global _LOCAL_CACHE
    if os.path.exists(_CACHE_FILE):
        try:
            with open(_CACHE_FILE, "rb") as f:
                _LOCAL_CACHE = pickle.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")
            _LOCAL_CACHE = {}
    else:
        _LOCAL_CACHE = {}


def _save_cache():
    global _LOCAL_CACHE
    os.makedirs(os.path.dirname(_CACHE_FILE), exist_ok=True)
    try:
        with open(_CACHE_FILE, "wb") as f:
            pickle.dump(_LOCAL_CACHE, f)
    except Exception as e:
        print(f"Error saving cache: {e}")


def _expand_abbreviations(text: str) -> str:
    expanded = text
    for acronym, phrase in ABBREVIATIONS.items():
        expanded = re.sub(rf"\b{re.escape(acronym)}\b", phrase, expanded)
    return expanded


def semantic_similarity(left: str, right: str) -> float:
    try:
        from sentence_transformers import util
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        left_emb = model.encode(left, convert_to_tensor=True)
        right_emb = model.encode(right, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(left_emb, right_emb).item()
        return round(float(similarity), 4)
    except Exception:
        return 0.0


def init_cache():
    global _CACHE_READY
    if _CACHE_READY:
        return
    _load_cache()
    _CACHE_READY = True


def set_similarity_threshold(threshold: float) -> None:
    global _SIMILARITY_THRESHOLD
    _SIMILARITY_THRESHOLD = max(0.0, min(1.0, float(threshold)))


def _compute_similarity(query1: str, query2: str) -> float:
    """Compute Jaccard similarity between two normalized queries (0-1)"""
    tokens1 = set(query1.split())
    tokens2 = set(query2.split())
    
    if not tokens1 or not tokens2:
        return 1.0 if query1 == query2 else 0.0
    
    intersection = len(tokens1 & tokens2)
    union = len(tokens1 | tokens2)
    
    return intersection / union if union > 0 else 0.0


def clear_cache() -> None:
    global _LOCAL_CACHE
    _LOCAL_CACHE = {}
    if os.path.exists(_CACHE_FILE):
        try:
            os.remove(_CACHE_FILE)
        except Exception as e:
            print(f"Error clearing cache: {e}")
    init_cache()


def get_cached_response(query: str, threshold: float = None):
    """Get cached response for a query using similarity-based matching"""
    init_cache()
    if threshold is not None:
        set_similarity_threshold(threshold)
    
    normalized = normalize_query(query)
    
    # Find best matching cached query above threshold
    best_match = None
    best_similarity = 0.0
    
    for cached_query, response in _LOCAL_CACHE.items():
        similarity = _compute_similarity(normalized, cached_query)
        if similarity >= _SIMILARITY_THRESHOLD and similarity > best_similarity:
            best_match = response
            best_similarity = similarity
    
    return best_match


def save_cached_response(query: str, response: str) -> None:
    """Save response to cache"""
    init_cache()
    normalized = normalize_query(query)
    _LOCAL_CACHE[normalized] = response
    _save_cache()

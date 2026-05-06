import os
import re

from gptcache import Config, cache
from gptcache.adapter.api import get, put
from gptcache.embedding.string import to_embeddings
from gptcache.manager import manager_factory
from gptcache.processor.pre import get_prompt
from gptcache.similarity_evaluation import ExactMatchEvaluation


_CACHE_READY = False


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
    text = re.sub(r"[?!.:,;]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def init_cache():
    global _CACHE_READY

    if _CACHE_READY:
        return

    data_dir = os.path.join(os.path.dirname(__file__), "gptcache_data")

    cache.init(
        pre_embedding_func=get_prompt,
        embedding_func=to_embeddings,
        data_manager=manager_factory("map", data_dir=data_dir),
        similarity_evaluation=ExactMatchEvaluation(),
        config=Config(similarity_threshold=0.90),
    )

    _CACHE_READY = True


def get_cached_response(query: str):
    init_cache()
    return get(normalize_query(query))


def save_cached_response(query: str, response: str):
    init_cache()
    put(normalize_query(query), response)
    cache.flush()

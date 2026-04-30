import os

from gptcache import Config, cache
from gptcache.adapter.api import get, put
from gptcache.embedding.string import to_embeddings
from gptcache.manager import manager_factory
from gptcache.processor.pre import get_prompt
from gptcache.similarity_evaluation import ExactMatchEvaluation


_CACHE_READY = False


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
    return get(query)


def save_cached_response(query: str, response: str):
    init_cache()
    put(query, response)
    cache.flush()

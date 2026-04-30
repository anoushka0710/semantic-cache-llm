from gptcache import cache
from gptcache.embedding import Onnx
from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

def init_cache():
    cache.init(
        embedding_func=Onnx(),
        similarity_evaluation=SearchDistanceEvaluation(),
    )
    cache.set_similarity_threshold(0.90)

def get_cache():
    return cache
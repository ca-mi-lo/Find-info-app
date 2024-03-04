import pickle
from hashlib import sha1
from typing import Tuple
from streamlit.runtime.state import SessionStateProxy

try:
    from elasticsearch import Elasticsearch

    is_elasticsearch_available = True
except ImportError:
    is_elasticsearch_available = False


def dict_to_sha1(d: dict) -> str:
    pickled_dict = pickle.dumps(d)

    return sha1(pickled_dict).hexdigest()


class BaseFeedback:
    def __init__(self):
        pass

    def _build_feedback_doc(self, sessionInfo: SessionStateProxy) -> Tuple[str, dict]:
        feedback_doc = {
            "answer": sessionInfo.debug.get("answer"),
            "doc_size": sessionInfo.get("doc_size"),
            "filehash": sessionInfo.index.get("file_hash"),
            "k_docs": sessionInfo.get("max_frags"),
            "model": sessionInfo.get("model"),
            "embedding_model": sessionInfo.get("embedding_model"),
            "overlap_ratio": sessionInfo.get("doc_overlap"),
            "question": sessionInfo.get("question"),
            "task": sessionInfo.get("task"),
            "temperature": sessionInfo.get("temperature"),
        }
        hash = dict_to_sha1(feedback_doc)

        return hash, feedback_doc

    def send(self, score: int, sessionInfo: SessionStateProxy) -> bool:
        return True


class ESFeedback(BaseFeedback):
    def __init__(self, host: str, port: int, index: str):
        if not is_elasticsearch_available:
            raise ImportError("elasticsearch package not found, please install it.")
        conn_str = f"{host}:{port}"
        self.es = Elasticsearch(hosts=[conn_str], max_retries=5)
        self.index = index

    def send(self, score: int, sessionInfo: SessionStateProxy) -> bool:
        id, feedback_doc = self._build_feedback_doc(sessionInfo)
        feedback_doc.update({"score": score})
        try:
            resp = self.es.index(index=self.index, id=id, body=feedback_doc)
            if resp.meta.status in [200, 201]:
                return True
            return False
        except elasticsearch.ConnectionError:
            return False

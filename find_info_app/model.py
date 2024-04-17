import hashlib
from time import time as now
from typing import IO, Any, Optional

import langchain_core
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts.prompt import PromptTemplate
from langchain_community.vectorstores import Chroma

from .pdf import MyAppPDFLoader
from . import ai
from .prompts import documents_to_str

store = Chroma()

def index_file(
    f: IO[bytes], filename: str, doc_size: int = 250, doc_overlap: int = 0
) -> dict:
    h = hashlib.sha1(usedforsecurity = False)
    h.update(f.read())
    sha = h.hexdigest()
    filesize = f.tell()
    f.seek(0)
    pdf_loader = MyAppPDFLoader(f, source = filename)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = doc_size, chunk_overlap = doc_overlap
    )
    t0 = now()  # load_docs
    data = pdf_loader.load_and_split(text_splitter=text_splitter)
    t1 = now()

    embedding = ai.get_embedding()
    store = Chroma.from_documents(data, embedding)

    t2 = now()
    summary_tmpl = PromptTemplate.from_template(
        """
    Describe the document from which the fragment is extracted. Omit any details.
    Text:{doc}
    """
    )
    summary = ai.complete(
        summary_tmpl.format(doc=data[0].page_content), temperature=0.1
    )
    t3 = now()

    index = {
        "doc_size": doc_size,
        "doc_overlap": doc_overlap,
        "n_docs": len(data),
        "store": store,
        "summary": summary,
        "filename": filename,
        "metadata":data[0].metadata['source'],
        "file_hash": sha,
        "filesize": filesize,
        "model": ai.BASE_MODEL,  # TODO: fix this line
        "profiling": {"load_docs": t1 - t0, "embed_docs": t2 - t1, "summary": t3 - t2},
    }

    return index


def query(
    text: str,
    task: str,
    index: dict,
    temperature: float = 0.2,
    max_frags: int = 5
) -> dict:
    out: dict[str, Any] = {"run": now()}

    db: Chroma = index["store"]

    embedding = ai.get_embedding(task_type='retrieval_query')

    t0 = now()
    query_vector = embedding.embed_query(text)
    selected_docs = db.max_marginal_relevance_search_by_vector(
            embedding= query_vector,
            k=max_frags,
            lambda_mult=0.2)
    selected_docs = documents_to_str(selected_docs)
    t1 = now()
    context_len = ai.get_token_count(selected_docs)

    prompt = PromptTemplate.from_template(
        """{task}
    {selected_docs}
    Question: {question} 
    The answer is:
    """
    )

    msg = prompt.format(task=task, selected_docs=selected_docs, question=text)

    t2 = now()
    resp = ai.complete(msg, temperature)
    t3 = now()

    out = {
        "msg": msg,
        "text": resp,
        "context_lenght": context_len,
        "profiling": {"retrive_docs": t1 - t0, "reasoning_time": t3 - t2},
    }

    return out
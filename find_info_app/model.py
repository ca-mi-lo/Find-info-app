import hashlib
from time import time as now
from typing import IO

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts.prompt import PromptTemplate
from langchain_community.vectorstores import Chroma

from .pdf import MyAppPDFLoader
from . import ai


def index_file(f: IO[bytes], filename: str,
               doc_size: int=250, doc_overlap: int=0) -> dict:
    h = hashlib.sha1(usedforsecurity=False)
    h.update(f.read())
    sha = h.hexdigest()
    filesize = f.tell()
    f.seek(0)
    pdf_loader = MyAppPDFLoader(f, source=filename)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=doc_size, 
                                                   chunk_overlap=doc_overlap)
    t0 = now() # load_docs
    data = pdf_loader.load_and_split(text_splitter=text_splitter)
    t1 = now()

    embedding = ai.get_embedding() 

    store = Chroma.from_documents(data, embedding)

    t2 = now()
    summary_tmpl = PromptTemplate.from_template(
        '''Describe the document from which the fragment is extracted. Omit any details.
        Text:{doc}''')
    summary = ai.complete(summary_tmpl.format(doc=data[0].page_content))
    t3 = now()

    index = {
        'doc_size': doc_size,
        'doc_overlap': doc_overlap,
        'n_docs': len(data),
        'store': store,
        'summary': summary,
        'docs': data,
        'filename': filename,
        'file_hash': f'sha1: {sha}',
        'filesize': filesize,
        'model': ai.BASE_MODEL, # TODO: fix this line
        'profiling': {'load_docs': t1-t0, 'embed_docs': t2-t1, 'summary': t3-t2} 
    }

    return index


def query():
    pass

from functools import partial
from typing import Sequence

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate, format_document

TASK = {
    "V1": (
        "Answer the question using the text below. Use the text provided as"
        " a context"
    )
}


def documents_to_str(docs: Sequence[Document], sep: str = "\n") -> str:
    new_documents = []
    for idx, doc in enumerate(docs):
        new_doc = Document(
            page_content=doc.page_content, metadata={"idx": idx + 1, **doc.metadata}
        )

        new_documents.append(new_doc)

    transform_prompt = PromptTemplate.from_template("Fragment {idx}: {page_content}")
    out = [format_document(doc, transform_prompt) for doc in new_documents]

    return sep.join(out)

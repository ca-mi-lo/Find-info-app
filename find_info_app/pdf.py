from typing import IO, Iterator, List

from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
from langchain_community.document_loaders.blob_loaders import Blob
from langchain_community.document_loaders.parsers.pdf import PyPDFParser

class MyAppPDFLoader(BaseLoader):
    
    def __init__(self,
                 file: IO[bytes],
                 source: str,
                 extract_images: bool= False) -> None:
        try:
            import pypdf  # noqa:F401
        except ImportError:
            raise ImportError(
                "pypdf package not found, please install it with " "`pip install pypdf`"
            ) 
        self.parser = PyPDFParser(password=None, extract_images=extract_images)
        self.metadata = {'source': source}
        self.pdf_data = file.read()

    def load(self) -> List[Document]:
        return list(self.lazy_load())

    def lazy_load(self) -> Iterator[Document]:
         blob = Blob.from_data(self.pdf_data, metadata=self.metadata)

         yield from self.parser.parse(blob)


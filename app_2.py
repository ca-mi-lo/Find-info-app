from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from chromadb import Client
import streamlit as st
with st.form("my-form", clear_on_submit=True):
        file = st.file_uploader("upload file")
        submitted = st.form_submit_button("submit")

#client = HttpClient(settings={"allow_reset": True})


doc1 = Document("hola mundo", metadata={"fn": "archivo1"})
doc2 = Document("hola soy Juan", metadata={"fn": "archivo2"})
doc3 = Document("hola mundo 2", metadata={"fn": "archivo1"})
doc4 = Document("hola mundo 3", metadata={"fn": "archivo1"})
embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
db = Chroma.from_documents([doc1, doc2, doc3, doc4], embedding)
#print(db)
print(db._collection.count())
docs_to_delete = db.get(where={"fn":"archivo1"})
db.delete(docs_to_delete["ids"])
print("After delete ids:")
print(db._collection.count())
print("After delete collection:")
db.delete_collection()
db = Chroma.from_documents([doc1, doc2], embedding)
print("After adding new elemets:")
print(db._collection.count())
print(db._collection.metadata)
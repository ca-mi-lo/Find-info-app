from langchain_google_genai.llms import GoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

BASE_MODEL = 'gemini-pro'
BASE_EMBEDDING_MODEL = 'models/embedding-001'


def get_embedding(model: str=BASE_EMBEDDING_MODEL):
    return GoogleGenerativeAIEmbeddings(model=model,
                                        task_type='retrieval_query')


def complete(text: str, **kwargs:str):
    model = kwargs.get('model', BASE_MODEL)
    llm = GoogleGenerativeAI(model=model)

    resp = llm.invoke(text)
    
    return resp

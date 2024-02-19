from langchain_google_genai.llms import GoogleGenerativeAI
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings

BASE_MODEL = "gemini-pro"
BASE_EMBEDDING_MODEL = "models/embedding-001"


def get_embedding(model: str = BASE_EMBEDDING_MODEL):
    return GoogleGenerativeAIEmbeddings(model=model, task_type="retrieval_query")


def get_token_count(text: str, **kwargs: str) -> int:
    model = kwargs.get("model", BASE_MODEL)
    llm = GoogleGenerativeAI(model=model)

    return llm.get_num_tokens(text)


def complete(text: str, temperature: float = 0.0, **kwargs: str):
    model = kwargs.get("model", BASE_MODEL)
    llm = GoogleGenerativeAI(model=model, temperature=temperature)

    resp = llm.invoke(text)

    return resp

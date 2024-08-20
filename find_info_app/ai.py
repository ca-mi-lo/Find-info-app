from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

AVAILABLE_EMBEDDINGS = ["models/embedding-001"]
AVAILABLE_MODELS = ["gemini-pro"]
BASE_MODEL = AVAILABLE_MODELS[0]
BASE_EMBEDDING_MODEL = AVAILABLE_EMBEDDINGS[0]


def get_embedding(
    model: str = BASE_EMBEDDING_MODEL, task_type: str = "retrieval_document"
):
    return GoogleGenerativeAIEmbeddings(model=model, task_type=task_type)


def get_token_count(text: str, **kwargs: str) -> int:
    model = kwargs.get("model", BASE_MODEL)
    llm = GoogleGenerativeAI(model=model)

    return llm.get_num_tokens(text)


def complete(text: str, temperature: float = 0.0, **kwargs: str):
    model = kwargs.get("model", BASE_MODEL)
    llm = GoogleGenerativeAI(model=model, temperature=temperature)

    resp = llm.invoke(text)

    return resp

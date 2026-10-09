from functools import lru_cache

from ollama import Client

from app.core.config import settings


EMBEDDING_DIMENSION = 768

@lru_cache(maxsize=1)
def get_ollama_client() -> Client:
    return Client(
        host=settings.ollama_base_url
    )

def embed_texts(
        texts: list[str],
)->list[list[float]]:
     if not texts:
        return []

     client = get_ollama_client()

     prepared_texts = [
        f"search_document: {text}"
        for text in texts
    ]

     response = client.embed(
         model=settings.embedding_model,
         input=prepared_texts,
     )

     embeddings = response.embeddings

     for vector in embeddings:
         if len(vector) != EMBEDDING_DIMENSION:
             raise ValueError(
                "Unexpected embedding dimension. "
                f"Expected {EMBEDDING_DIMENSION}, "
                f"received {len(vector)}."
            )
         
     return embeddings

def embed_query(
        query:str,
)->list[float]:
    query = query.strip()

    if not query:
        raise ValueError(
            "Search query cannot be empty."
        )
    client = get_ollama_client()

    response = client.embed(
        model=settings.embedding_model,
        input=f"search_query:{query}"
    )

    vector = response.embeddings[0]

    if len(vector) != EMBEDDING_DIMENSION:
        raise ValueError(
            "Unexpected embedding dimension. "
            f"Expected {EMBEDDING_DIMENSION}, "
            f"received {len(vector)}."
        )

    return vector
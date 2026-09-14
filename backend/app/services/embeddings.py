import math

from fastapi import HTTPException, status
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

from ..config import EMBEDDING_DIMENSIONS, EMBEDDING_MODEL, GEMINI_API_KEY

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GEMINI_API_KEY is not configured on the server",
        )
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0:
        return vector
    return [v / norm for v in vector]


def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Embed document chunks for storage (RETRIEVAL_DOCUMENT task type)."""
    if not chunks:
        return []

    client = _get_client()

    try:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=chunks,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=EMBEDDING_DIMENSIONS,
            ),
        )
    except (ClientError, ServerError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Embedding request to Gemini failed: {exc}",
        ) from exc

    # Non-default output dimensions are not pre-normalized by the API, so
    # normalize manually for consistent cosine similarity search.
    return [_normalize(list(embedding.values)) for embedding in response.embeddings]


def embed_query(question: str) -> list[float]:
    """Embed a user question for similarity search (RETRIEVAL_QUERY task type)."""
    client = _get_client()

    try:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=question,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=EMBEDDING_DIMENSIONS,
            ),
        )
    except (ClientError, ServerError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Embedding request to Gemini failed: {exc}",
        ) from exc

    return _normalize(list(response.embeddings[0].values))

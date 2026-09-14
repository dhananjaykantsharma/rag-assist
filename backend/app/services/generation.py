from fastapi import HTTPException, status
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

from ..config import GEMINI_API_KEY, GEMINI_TEXT_MODEL

_client: genai.Client | None = None

SYSTEM_INSTRUCTION = (
    "You are a helpful assistant that answers questions using ONLY the "
    "provided document excerpts as context. If the answer is not contained "
    "in the context, say you don't have enough information from the "
    "document to answer. Be concise."
)


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


def generate_answer(question: str, context_chunks: list[str]) -> str:
    client = _get_client()

    context = "\n\n---\n\n".join(context_chunks) if context_chunks else "(no relevant context found)"
    prompt = f"Context:\n{context}\n\nQuestion: {question}"

    try:
        response = client.models.generate_content(
            model=GEMINI_TEXT_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.2,
                max_output_tokens=1024,
            ),
        )
    except (ClientError, ServerError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Answer generation request to Gemini failed: {exc}",
        ) from exc

    return response.text or ""

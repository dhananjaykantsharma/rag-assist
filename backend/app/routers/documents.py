from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..config import MAX_DOCUMENT_WORDS, QA_TOP_K_CHUNKS
from ..database import get_db
from ..models import Document, DocumentChunk, User
from ..schemas import AskRequest, AskResponse, DocumentOut, SourceChunk
from ..security import get_current_user
from ..services.chunking import chunk_text
from ..services.embeddings import embed_chunks, embed_query
from ..services.generation import generate_answer
from ..services.text_extraction import extract_text

router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.get("", response_model=list[DocumentOut])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    documents = (
        db.query(Document)
        .filter(Document.owner_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )

    chunk_counts = dict(
        db.query(DocumentChunk.document_id, func.count(DocumentChunk.id))
        .join(Document, Document.id == DocumentChunk.document_id)
        .filter(Document.owner_id == current_user.id)
        .group_by(DocumentChunk.document_id)
        .all()
    )

    return [
        DocumentOut(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            word_count=document.word_count,
            chunk_count=chunk_counts.get(document.id, 0),
            created_at=document.created_at,
        )
        for document in documents
    ]


def _get_owned_document(document_id: int, current_user: User, db: Session) -> Document:
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.owner_id == current_user.id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = await file.read()
    text = extract_text(file, data)

    word_count = len(text.split())
    if word_count > MAX_DOCUMENT_WORDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document has {word_count} words, which exceeds the {MAX_DOCUMENT_WORDS} word limit",
        )

    chunks = chunk_text(text)
    vectors = embed_chunks(chunks)

    document = Document(
        owner_id=current_user.id,
        filename=file.filename or "untitled",
        content_type=file.content_type or "application/octet-stream",
        word_count=word_count,
    )
    db.add(document)
    db.flush()

    for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
        db.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=vector,
            )
        )

    db.commit()
    db.refresh(document)

    return DocumentOut(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        word_count=document.word_count,
        chunk_count=len(chunks),
        created_at=document.created_at,
    )


@router.post("/{document_id}/ask", response_model=AskResponse)
def ask_document(
    document_id: int,
    payload: AskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = _get_owned_document(document_id, current_user, db)

    query_vector = embed_query(payload.question)

    distance = DocumentChunk.embedding.cosine_distance(query_vector)
    results = (
        db.query(DocumentChunk, distance.label("distance"))
        .filter(DocumentChunk.document_id == document.id)
        .order_by(distance)
        .limit(QA_TOP_K_CHUNKS)
        .all()
    )

    if not results:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This document has no processed content to search yet",
        )

    context_chunks = [chunk.content for chunk, _ in results]
    answer = generate_answer(payload.question, context_chunks)

    sources = [
        SourceChunk(
            chunk_id=chunk.id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            similarity=1 - dist,
        )
        for chunk, dist in results
    ]

    return AskResponse(answer=answer, sources=sources)

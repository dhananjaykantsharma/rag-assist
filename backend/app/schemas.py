from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    content_type: str
    word_count: int
    chunk_count: int
    created_at: datetime


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


class SourceChunk(BaseModel):
    chunk_id: int
    chunk_index: int
    content: str
    similarity: float


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]

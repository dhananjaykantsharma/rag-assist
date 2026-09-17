from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, documents

# Schema is managed by Alembic migrations (see backend/alembic) instead of
# being auto-created here.

app = FastAPI(title="RAG Assist API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://wonderful-forgiveness-production-5ded.up.railway.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(documents.router)


@app.get("/")
def root():
    return {"status": "ok"}

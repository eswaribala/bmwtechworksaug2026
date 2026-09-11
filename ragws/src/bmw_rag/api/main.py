from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from bmw_rag.agents.rag_agent import answer_question
from bmw_rag.services import reindex_documents

app = FastAPI(
    title="BMW Document RAG API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:5174","https://glorious-bassoon-6pvxpvv94w25rxj-5173.app.github.dev/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/ingest")
def ingest(client: str):
    try:
        return reindex_documents(client)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error


@app.post("/ask")
def ask(client: str, request: QuestionRequest):
    try:
        return answer_question(client, request.question)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error
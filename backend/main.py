# backend/main.py
#
# The FastAPI backend: skill browsing, semantic search, and the RAG-grounded
# chat endpoint. This is the only layer that talks to the LLM (Groq) — the
# frontend never sees an API key.

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel

from cache import SimilarityCache
from knowledge_base import SKILLS, Skill
from rag import search

# WHY load_dotenv() here rather than relying on the shell environment: keeps
# `uvicorn main:app` runnable directly in local dev without the developer
# having to export GROQ_API_KEY manually every session.
load_dotenv()

app = FastAPI(title="Career Skill Navigator API")

# WHY allow all origins for now: the frontend's exact Vercel URL isn't known
# yet (Step 14). Locking this down to a specific origin is a one-line change
# once that URL exists — tracked, not forgotten.
# ALTERNATIVE: hardcode localhost:3000 now — would break the deployed
# frontend until someone remembers to update it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])
_chat_cache = SimilarityCache()

_GROQ_MODEL = "llama-3.3-70b-versatile"

_SKILLS_BY_ID: dict[str, Skill] = {skill["id"]: skill for skill in SKILLS}

_SYSTEM_PROMPT = (
    "You are a career advisor for software engineering skills. Answer ONLY "
    "using the skill information provided in the context below — if the "
    "context doesn't cover what the user asked, say so instead of guessing. "
    "Keep answers concise and reference specific skills by name."
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str
    sources: list[str]
    cached: bool


class SearchRequest(BaseModel):
    query: str
    top_k: int = 4


def _build_context(skills: list[Skill]) -> str:
    """Render retrieved skills into plain text for the system prompt.

    WHY plain text instead of JSON: the model reads this as prose context,
    not structured data it needs to parse — JSON would waste tokens on
    punctuation the model doesn't need to reproduce.
    """
    blocks = []
    for skill in skills:
        blocks.append(
            f"- {skill['name']} ({skill['level']}, ~{skill['estimated_weeks']} weeks): "
            f"{skill['description']} Job relevance: {skill['job_relevance']}"
        )
    return "\n".join(blocks)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/skills")
def get_skills() -> list[Skill]:
    return SKILLS


@app.get("/skills/{skill_id}")
def get_skill(skill_id: str) -> Skill:
    skill = _SKILLS_BY_ID.get(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail=f"Unknown skill id '{skill_id}'")
    return skill


@app.post("/search")
def search_skills(request: SearchRequest) -> list[Skill]:
    return search(request.query, top_k=request.top_k)


@app.post("/chat")
def chat(request: ChatRequest) -> ChatResponse:
    cached_response = _chat_cache.get(request.message)
    if cached_response is not None:
        return ChatResponse(response=cached_response, sources=[], cached=True)

    retrieved = search(request.message, top_k=4)
    context = _build_context(retrieved)

    messages = [{"role": "system", "content": f"{_SYSTEM_PROMPT}\n\nContext:\n{context}"}]
    messages.extend({"role": m.role, "content": m.content} for m in request.history)
    messages.append({"role": "user", "content": request.message})

    completion = _groq_client.chat.completions.create(
        model=_GROQ_MODEL,
        messages=messages,
    )
    response_text = completion.choices[0].message.content

    _chat_cache.set(request.message, response_text)

    return ChatResponse(
        response=response_text,
        sources=[skill["id"] for skill in retrieved],
        cached=False,
    )

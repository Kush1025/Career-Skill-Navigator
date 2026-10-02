# Career Skill Navigator

A RAG-powered AI career advisor that helps students and job-seekers navigate
software engineering learning paths, grounded in a curated knowledge base of
50+ skills.

## Status

🚧 In development. The backend is complete and tested; the frontend is next.

- ✅ Knowledge base — 59 curated software engineering skills
- ✅ RAG engine — ChromaDB vector index over sentence-transformers embeddings
- ✅ Semantic response cache — cosine-similarity lookup in front of the LLM
- ✅ FastAPI API — `/health`, `/skills`, `/skills/{id}`, `/search`, `/chat`
- ✅ Test suite — 32 pytest tests, LLM calls mocked
- ⬜ Next.js frontend
- ⬜ Deployment (Render + Vercel)

## Tech Stack

- **Backend:** FastAPI (Python) + ChromaDB + sentence-transformers (all-MiniLM-L6-v2)
- **LLM:** Llama 3.3 70B via the Groq API
- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind CSS
- **Deploy:** Render (backend) + Vercel (frontend), both free tier

Every component was chosen to run at $0: embeddings run locally, the vector
store is in-process, and the cache is in-memory.

## How `/chat` works

1. **Cache check** — the incoming question is embedded and compared against
   previously answered questions by cosine similarity. A hit returns
   immediately, skipping the LLM entirely.
2. **Retrieve** — on a miss, the query embedding is used to pull the top-4
   most relevant skills out of ChromaDB.
3. **Ground** — those skills are injected into the system prompt, which
   instructs the model to answer *only* from the provided context.
4. **Generate** — Groq returns the answer, and the retrieved skill IDs come
   back as `sources` so every response is traceable.

## Running the backend locally

```bash
cd backend
python -m venv venv
venv/Scripts/activate          # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env           # then add your free Groq API key

uvicorn main:app --reload      # docs at http://127.0.0.1:8000/docs
```

Run the tests with `python -m pytest` from the `backend/` directory.

The ChromaDB index builds itself on first import and rebuilds automatically
whenever the knowledge base changes, so there is no separate indexing step.

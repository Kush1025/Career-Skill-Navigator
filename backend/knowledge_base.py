# backend/knowledge_base.py
#
# The curated, hand-written knowledge base the whole RAG pipeline is grounded in.
# Every skill below follows the schema locked in CLAUDE.md. This module is the
# single source of truth: Step 3 embeds and indexes it into ChromaDB, and
# Step 5's /skills endpoints serve it directly.
#
# WHY a plain Python list of dicts instead of JSON or a database: the data is
# static, small (~60 rows), and benefits from IDE type-checking/autocomplete
# when imported elsewhere. A database would add a dependency and a migration
# story this project doesn't need.
# ALTERNATIVE: a JSON file would decouple content from code, but loses type
# hints and needs a loader step for no real benefit at this scale.

from typing import Literal, TypedDict


class Skill(TypedDict):
    """One entry in the knowledge base. Schema locked in CLAUDE.md."""

    id: str
    name: str
    category: Literal[
        "Programming Language",
        "Backend",
        "Frontend Framework",
        "Full-Stack Framework",
        "Database",
        "AI/ML",
        "AI/ML Infrastructure",
        "DevOps",
        "Cloud",
        "Developer Tool",
        "Software Engineering",
        "Computer Science",
    ]
    description: str
    level: Literal["beginner", "intermediate", "advanced"]
    estimated_weeks: int
    prerequisites: list[str]
    leads_to: list[str]
    use_cases: list[str]
    resources: list[str]
    job_relevance: str


# ---------------------------------------------------------------------------
# Programming Languages
# ---------------------------------------------------------------------------
_PROGRAMMING_LANGUAGES: list[Skill] = [
    {
        "id": "python",
        "name": "Python",
        "category": "Programming Language",
        "description": "A readable, general-purpose language with a huge ecosystem "
        "spanning web backends, data science, and AI/ML. Its gentle syntax makes it "
        "a common first language and its libraries make it a common last one too.",
        "level": "beginner",
        "estimated_weeks": 6,
        "prerequisites": [],
        "leads_to": ["fastapi", "django", "machine-learning-fundamentals", "data-structures-algorithms"],
        "use_cases": ["Web backends", "Data analysis", "Automation scripting", "ML/AI research"],
        "resources": ["Official Python Tutorial (docs.python.org)", "freeCodeCamp Python course", "Automate the Boring Stuff with Python (free online)"],
        "job_relevance": "One of the most requested languages across backend, data, and AI/ML job postings.",
    },
    {
        "id": "javascript",
        "name": "JavaScript",
        "category": "Programming Language",
        "description": "The language of the web browser, and via Node.js, of a huge "
        "share of backend services too. Essential for any frontend work.",
        "level": "beginner",
        "estimated_weeks": 6,
        "prerequisites": ["html-css"],
        "leads_to": ["typescript", "react", "express-js"],
        "use_cases": ["Interactive web pages", "Node.js backends", "Browser extensions"],
        "resources": ["MDN JavaScript Guide", "freeCodeCamp JavaScript course", "javascript.info"],
        "job_relevance": "Required for essentially all frontend roles and common in full-stack postings.",
    },
    {
        "id": "typescript",
        "name": "TypeScript",
        "category": "Programming Language",
        "description": "JavaScript with static types, catching entire classes of bugs "
        "before code ever runs. The default choice for serious frontend and Node projects today.",
        "level": "intermediate",
        "estimated_weeks": 3,
        "prerequisites": ["javascript"],
        "leads_to": ["react", "nextjs", "express-js"],
        "use_cases": ["Type-safe frontend apps", "Large Node.js codebases", "Shared API contracts"],
        "resources": ["Official TypeScript Handbook (typescriptlang.org)", "Total TypeScript free tier"],
        "job_relevance": "Increasingly a default expectation, not a bonus, in modern frontend/full-stack postings.",
    },
    {
        "id": "java",
        "name": "Java",
        "category": "Programming Language",
        "description": "A statically typed, verbose-but-battle-tested language that "
        "still dominates enterprise backends, especially at larger and older companies.",
        "level": "intermediate",
        "estimated_weeks": 6,
        "prerequisites": [],
        "leads_to": ["spring-boot", "data-structures-algorithms"],
        "use_cases": ["Enterprise backend systems", "Android (via Kotlin interop)", "Large-scale distributed systems"],
        "resources": ["Oracle's official Java Tutorials", "freeCodeCamp Java course"],
        "job_relevance": "Still one of the top languages by job volume, concentrated in enterprise and fintech.",
    },
    {
        "id": "go",
        "name": "Go",
        "category": "Programming Language",
        "description": "A simple, fast, compiled language built for concurrency, "
        "designed by Google. Popular for infrastructure and cloud-native tooling.",
        "level": "intermediate",
        "estimated_weeks": 4,
        "prerequisites": [],
        "leads_to": ["kubernetes", "microservices"],
        "use_cases": ["Cloud infrastructure tools", "High-throughput microservices", "CLI tools"],
        "resources": ["A Tour of Go (official, interactive)", "Go by Example"],
        "job_relevance": "High demand in cloud/infrastructure roles; most cloud-native tooling (Docker, Kubernetes) is written in it.",
    },
    {
        "id": "sql",
        "name": "SQL",
        "category": "Programming Language",
        "description": "The query language for relational databases. Arguably the "
        "single most universally required technical skill in software engineering.",
        "level": "beginner",
        "estimated_weeks": 3,
        "prerequisites": [],
        "leads_to": ["postgresql", "database-design"],
        "use_cases": ["Querying/reporting on relational data", "Data analysis", "Backend persistence"],
        "resources": ["SQLBolt (free interactive)", "Mode's SQL Tutorial", "PostgreSQL official docs tutorial"],
        "job_relevance": "Appears in the vast majority of backend, data, and analytics job postings regardless of stack.",
    },
    {
        "id": "cpp",
        "name": "C++",
        "category": "Programming Language",
        "description": "A low-level, high-performance systems language giving direct "
        "control over memory. The backbone of game engines, and a staple of technical interviews.",
        "level": "advanced",
        "estimated_weeks": 8,
        "prerequisites": [],
        "leads_to": ["data-structures-algorithms", "operating-systems"],
        "use_cases": ["Game engines", "High-frequency trading systems", "Embedded systems"],
        "resources": ["learncpp.com (free, comprehensive)", "cppreference.com"],
        "job_relevance": "Concentrated in performance-critical domains (gaming, finance, embedded); also a common DSA-interview language.",
    },
]

# ---------------------------------------------------------------------------
# Frontend Frameworks
# ---------------------------------------------------------------------------
_FRONTEND: list[Skill] = [
    {
        "id": "html-css",
        "name": "HTML & CSS",
        "category": "Frontend Framework",
        "description": "The structural and visual foundation of every web page. "
        "Every frontend framework is ultimately generating and styling these two things.",
        "level": "beginner",
        "estimated_weeks": 4,
        "prerequisites": [],
        "leads_to": ["javascript", "react"],
        "use_cases": ["Static web pages", "Styling any web UI", "Email templates"],
        "resources": ["MDN HTML/CSS docs", "freeCodeCamp Responsive Web Design"],
        "job_relevance": "A baseline requirement for literally every frontend and full-stack role.",
    },
    {
        "id": "react",
        "name": "React",
        "category": "Frontend Framework",
        "description": "A component-based library for building UIs out of reusable, "
        "composable pieces. The dominant frontend paradigm across the industry.",
        "level": "intermediate",
        "estimated_weeks": 5,
        "prerequisites": ["javascript", "html-css"],
        "leads_to": ["nextjs", "frontend-state-management"],
        "use_cases": ["Single-page applications", "Dashboards", "Interactive UIs"],
        "resources": ["Official React docs (react.dev)", "freeCodeCamp React course"],
        "job_relevance": "The most commonly requested frontend framework in job postings today.",
    },
    {
        "id": "vue",
        "name": "Vue.js",
        "category": "Frontend Framework",
        "description": "A progressive, approachable component framework often "
        "considered easier to learn than React while covering similar ground.",
        "level": "intermediate",
        "estimated_weeks": 4,
        "prerequisites": ["javascript", "html-css"],
        "leads_to": ["frontend-state-management"],
        "use_cases": ["Single-page applications", "Progressive enhancement of existing sites"],
        "resources": ["Official Vue.js docs and tutorial (vuejs.org)"],
        "job_relevance": "Smaller market share than React but consistently requested, especially in Europe and Asia.",
    },
    {
        "id": "frontend-state-management",
        "name": "Frontend State Management",
        "category": "Frontend Framework",
        "description": "Patterns and libraries (Context, Redux, Zustand, Pinia) for "
        "managing shared application state across components as UIs grow beyond trivial size.",
        "level": "intermediate",
        "estimated_weeks": 2,
        "prerequisites": ["react"],
        "leads_to": ["nextjs"],
        "use_cases": ["Complex multi-component apps", "Shared auth/user state", "Real-time UIs"],
        "resources": ["Official Redux Toolkit docs", "Zustand GitHub README (concise, free)"],
        "job_relevance": "Commonly probed in frontend interviews once a candidate is past framework basics.",
    },
]

# ---------------------------------------------------------------------------
# Full-Stack Frameworks
# ---------------------------------------------------------------------------
_FULL_STACK: list[Skill] = [
    {
        "id": "nextjs",
        "name": "Next.js",
        "category": "Full-Stack Framework",
        "description": "A React framework adding server-side rendering, routing, "
        "and API routes out of the box. The industry-standard way to ship production React apps.",
        "level": "intermediate",
        "estimated_weeks": 4,
        "prerequisites": ["react", "typescript"],
        "leads_to": ["frontend-state-management"],
        "use_cases": ["Production web apps needing SEO/SSR", "Full-stack apps with API routes", "Static marketing sites"],
        "resources": ["Official Next.js docs and Learn course (nextjs.org/learn)"],
        "job_relevance": "The most commonly requested React meta-framework in current job postings.",
    },
    {
        "id": "django",
        "name": "Django",
        "category": "Full-Stack Framework",
        "description": "A batteries-included Python web framework with a built-in "
        "ORM, admin panel, and auth system. Optimized for shipping fast without gluing together libraries.",
        "level": "intermediate",
        "estimated_weeks": 5,
        "prerequisites": ["python", "sql"],
        "leads_to": ["orm-sqlalchemy", "rest-api-design"],
        "use_cases": ["Content-heavy web apps", "Admin-panel-driven internal tools", "Rapid MVP development"],
        "resources": ["Official Django Tutorial (docs.djangoproject.com)"],
        "job_relevance": "Common in Python-shop backend postings, especially where an admin panel or CMS-like feature is needed.",
    },
]

# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------
_BACKEND: list[Skill] = [
    {
        "id": "rest-api-design",
        "name": "REST API Design",
        "category": "Backend",
        "description": "Principles for designing predictable, resource-oriented "
        "HTTP APIs — status codes, verbs, versioning, pagination. The most common way services talk to each other.",
        "level": "beginner",
        "estimated_weeks": 2,
        "prerequisites": [],
        "leads_to": ["fastapi", "express-js", "graphql-apis"],
        "use_cases": ["Public/internal HTTP APIs", "Service-to-service communication"],
        "resources": ["Microsoft REST API Guidelines (free, GitHub)", "restfulapi.net"],
        "job_relevance": "A near-universal expectation for any backend role.",
    },
    {
        "id": "fastapi",
        "name": "FastAPI",
        "category": "Backend",
        "description": "A modern, async-first Python web framework with automatic "
        "OpenAPI docs and Pydantic-based validation. The go-to choice for Python ML/AI backends today.",
        "level": "intermediate",
        "estimated_weeks": 3,
        "prerequisites": ["python", "rest-api-design"],
        "leads_to": ["auth-fundamentals", "websockets"],
        "use_cases": ["ML/AI model-serving APIs", "High-performance async backends", "Microservices"],
        "resources": ["Official FastAPI docs (fastapi.tiangolo.com) — excellent and free"],
        "job_relevance": "Rapidly growing demand, especially at AI/ML-focused companies replacing Flask.",
    },
    {
        "id": "express-js",
        "name": "Express.js",
        "category": "Backend",
        "description": "A minimal, unopinionated Node.js web framework. The default "
        "way most JavaScript/TypeScript developers build backend HTTP servers.",
        "level": "beginner",
        "estimated_weeks": 3,
        "prerequisites": ["javascript", "rest-api-design"],
        "leads_to": ["auth-fundamentals", "microservices"],
        "use_cases": ["Node.js REST APIs", "Backend-for-frontend services"],
        "resources": ["Official Express.js docs and guide"],
        "job_relevance": "The most common Node.js backend framework named in JS full-stack postings.",
    },
    {
        "id": "spring-boot",
        "name": "Spring Boot",
        "category": "Backend",
        "description": "A convention-over-configuration framework for building "
        "production-grade Java applications quickly, handling dependency injection and boilerplate wiring.",
        "level": "intermediate",
        "estimated_weeks": 5,
        "prerequisites": ["java"],
        "leads_to": ["microservices"],
        "use_cases": ["Enterprise backend services", "Microservices in Java shops"],
        "resources": ["Official Spring Boot guides (spring.io/guides)"],
        "job_relevance": "The dominant Java backend framework in enterprise job postings.",
    },
    {
        "id": "graphql-apis",
        "name": "GraphQL",
        "category": "Backend",
        "description": "A query language for APIs letting clients request exactly "
        "the fields they need in a single round trip, instead of multiple REST calls.",
        "level": "intermediate",
        "estimated_weeks": 3,
        "prerequisites": ["rest-api-design"],
        "leads_to": [],
        "use_cases": ["Mobile apps needing minimal payloads", "APIs aggregating multiple backend services"],
        "resources": ["Official GraphQL docs (graphql.org/learn)"],
        "job_relevance": "A common secondary skill listed alongside REST at companies with complex client needs.",
    },
    {
        "id": "websockets",
        "name": "WebSockets",
        "category": "Backend",
        "description": "A persistent, full-duplex connection protocol enabling "
        "real-time, bidirectional communication between client and server — used for chat, live updates, and streaming.",
        "level": "intermediate",
        "estimated_weeks": 2,
        "prerequisites": ["fastapi"],
        "leads_to": [],
        "use_cases": ["Chat applications", "Live dashboards", "Streaming LLM responses"],
        "resources": ["MDN WebSockets API docs", "FastAPI WebSockets docs"],
        "job_relevance": "Commonly required for any real-time feature — chat, notifications, collaborative tools.",
    },
    {
        "id": "auth-fundamentals",
        "name": "Authentication & Authorization",
        "category": "Backend",
        "description": "The mechanisms (sessions, JWTs, OAuth) for verifying who a "
        "user is and what they're allowed to do. Gets everything wrong in production if rushed.",
        "level": "intermediate",
        "estimated_weeks": 3,
        "prerequisites": ["rest-api-design"],
        "leads_to": ["microservices"],
        "use_cases": ["User login systems", "Third-party OAuth sign-in", "API access control"],
        "resources": ["OWASP Authentication Cheat Sheet (free)", "Auth0's free blog guides"],
        "job_relevance": "A near-universal requirement; security-conscious auth implementation is a strong interview signal.",
    },
    {
        "id": "microservices",
        "name": "Microservices Architecture",
        "category": "Backend",
        "description": "Splitting a system into small, independently deployable "
        "services communicating over the network, trading simplicity for scalability and team autonomy.",
        "level": "advanced",
        "estimated_weeks": 4,
        "prerequisites": ["rest-api-design", "docker"],
        "leads_to": ["kubernetes", "distributed-systems"],
        "use_cases": ["Large-scale systems with independent teams", "Systems needing independent scaling per component"],
        "resources": ["microservices.io (free pattern catalog by Chris Richardson)"],
        "job_relevance": "Frequently discussed in system-design interviews at mid-to-large tech companies.",
    },
]

# ---------------------------------------------------------------------------
# Databases
# ---------------------------------------------------------------------------
_DATABASE: list[Skill] = [
    {
        "id": "postgresql",
        "name": "PostgreSQL",
        "category": "Database",
        "description": "A powerful, open-source relational database known for "
        "standards compliance and extensibility. The default relational DB choice for most new projects.",
        "level": "intermediate",
        "estimated_weeks": 3,
        "prerequisites": ["sql"],
        "leads_to": ["database-design", "orm-sqlalchemy"],
        "use_cases": ["Transactional application data", "Complex relational queries", "JSON + relational hybrid storage"],
        "resources": ["Official PostgreSQL Tutorial (postgresql.org/docs)"],
        "job_relevance": "The most commonly requested relational database in current backend job postings.",
    },
    {
        "id": "mongodb",
        "name": "MongoDB",
        "category": "Database",
        "description": "A document-oriented NoSQL database storing flexible, "
        "JSON-like records instead of rigid tables. Popular where schema flexibility matters more than strict relations.",
        "level": "beginner",
        "estimated_weeks": 2,
        "prerequisites": [],
        "leads_to": ["database-design"],
        "use_cases": ["Rapidly evolving schemas", "Content management systems", "Event/log storage"],
        "resources": ["Official MongoDB University (free courses)"],
        "job_relevance": "The most common NoSQL database named in full-stack JavaScript job postings (MERN/MEAN stacks).",
    },
    {
        "id": "redis",
        "name": "Redis",
        "category": "Database",
        "description": "An in-memory key-value store used for caching, session "
        "storage, rate limiting, and pub/sub — trading persistence guarantees for extreme speed.",
        "level": "intermediate",
        "estimated_weeks": 2,
        "prerequisites": [],
        "leads_to": [],
        "use_cases": ["Caching layers", "Session storage", "Rate limiting", "Real-time leaderboards"],
        "resources": ["Official Redis docs and free interactive tutorial (redis.io)"],
        "job_relevance": "The standard caching layer named in most backend architecture discussions and interviews.",
    },
    {
        "id": "database-design",
        "name": "Database Design & Normalization",
        "category": "Database",
        "description": "Principles for structuring tables, relationships, and "
        "indexes to keep data consistent and queries fast as an application grows.",
        "level": "intermediate",
        "estimated_weeks": 2,
        "prerequisites": ["sql"],
        "leads_to": ["system-design"],
        "use_cases": ["Designing schemas for new applications", "Refactoring slow or inconsistent data models"],
        "resources": ["Database Design for Mere Mortals (concepts summarized free online)", "PostgreSQL docs on indexing"],
        "job_relevance": "A frequent whiteboard-interview topic for backend and full-stack roles.",
    },
    {
        "id": "orm-sqlalchemy",
        "name": "ORMs (SQLAlchemy)",
        "category": "Database",
        "description": "Object-relational mappers let you interact with a "
        "relational database using Python objects instead of raw SQL strings, while still allowing raw SQL when needed.",
        "level": "intermediate",
        "estimated_weeks": 2,
        "prerequisites": ["postgresql", "python"],
        "leads_to": [],
        "use_cases": ["Type-safe database access in Python apps", "Schema migrations"],
        "resources": ["Official SQLAlchemy docs (1.x and 2.x tutorials)"],
        "job_relevance": "Commonly listed alongside FastAPI/Django/Flask in Python backend postings.",
    },
]

# ---------------------------------------------------------------------------
# AI / ML
# ---------------------------------------------------------------------------
_AI_ML: list[Skill] = [
    {
        "id": "machine-learning-fundamentals",
        "name": "Machine Learning Fundamentals",
        "category": "AI/ML",
        "description": "Core concepts — supervised/unsupervised learning, "
        "train/test splits, overfitting, evaluation metrics — underlying every ML system, regardless of framework.",
        "level": "intermediate",
        "estimated_weeks": 6,
        "prerequisites": ["python"],
        "leads_to": ["deep-learning", "nlp"],
        "use_cases": ["Predictive modeling", "Classification/regression problems", "Recommendation systems"],
        "resources": ["Andrew Ng's Machine Learning Specialization (audit free on Coursera)", "scikit-learn official docs"],
        "job_relevance": "A foundational requirement for any AI/ML or data science role.",
    },
    {
        "id": "deep-learning",
        "name": "Deep Learning",
        "category": "AI/ML",
        "description": "Neural networks with many layers, capable of learning "
        "complex patterns directly from raw data (images, text, audio) without hand-engineered features.",
        "level": "advanced",
        "estimated_weeks": 8,
        "prerequisites": ["machine-learning-fundamentals"],
        "leads_to": ["nlp", "pytorch"],
        "use_cases": ["Computer vision", "Speech recognition", "Large language models"],
        "resources": ["fast.ai Practical Deep Learning (free)", "deeplearning.ai courses (audit free)"],
        "job_relevance": "Core skill for ML engineer and AI research roles; growing demand tied to LLM adoption.",
    },
    {
        "id": "nlp",
        "name": "Natural Language Processing",
        "category": "AI/ML",
        "description": "Techniques for getting computers to process and generate "
        "human language — tokenization, embeddings, transformers, and the foundation modern LLMs are built on.",
        "level": "advanced",
        "estimated_weeks": 6,
        "prerequisites": ["machine-learning-fundamentals"],
        "leads_to": ["prompt-engineering", "embeddings"],
        "use_cases": ["Chatbots", "Text classification/summarization", "Search and retrieval systems"],
        "resources": ["Hugging Face NLP Course (free)", "Stanford CS224n lecture notes (free)"],
        "job_relevance": "Directly relevant to the current surge in LLM-application engineering roles.",
    },
    {
        "id": "prompt-engineering",
        "name": "Prompt Engineering",
        "category": "AI/ML",
        "description": "The practice of structuring inputs to LLMs to reliably "
        "get useful, well-formatted, and grounded outputs — part craft, part systematic experimentation.",
        "level": "beginner",
        "estimated_weeks": 2,
        "prerequisites": [],
        "leads_to": ["rag-systems", "llm-apis"],
        "use_cases": ["Building chatbots/assistants", "Structured data extraction from text", "Content generation pipelines"],
        "resources": ["Anthropic's official Prompt Engineering guide (free)", "OpenAI's Prompt Engineering guide (free)"],
        "job_relevance": "An increasingly explicit line item in AI-application-engineer job postings.",
    },
    {
        "id": "rag-systems",
        "name": "Retrieval-Augmented Generation (RAG)",
        "category": "AI/ML",
        "description": "An architecture pattern that grounds LLM responses in a "
        "retrieved knowledge base rather than relying purely on the model's training data — reduces hallucination and keeps answers current.",
        "level": "intermediate",
        "estimated_weeks": 3,
        "prerequisites": ["prompt-engineering", "embeddings"],
        "leads_to": [],
        "use_cases": ["Domain-specific Q&A assistants", "Internal knowledge-base search", "Customer support bots"],
        "resources": ["Anthropic's RAG documentation (free)", "LangChain RAG tutorial (free docs)"],
        "job_relevance": "One of the most commonly requested architecture patterns in current AI-engineering postings — this project itself is a RAG system.",
    },
    {
        "id": "pytorch",
        "name": "PyTorch",
        "category": "AI/ML",
        "description": "The dominant deep learning framework in research and "
        "increasingly in production, offering flexible, Python-native tensor computation and autograd.",
        "level": "advanced",
        "estimated_weeks": 5,
        "prerequisites": ["deep-learning"],
        "leads_to": [],
        "use_cases": ["Training custom neural networks", "Fine-tuning pretrained models"],
        "resources": ["Official PyTorch tutorials (pytorch.org/tutorials)"],
        "job_relevance": "The most commonly required deep learning framework in ML engineer/researcher postings.",
    },
]

# ---------------------------------------------------------------------------
# AI / ML Infrastructure
# ---------------------------------------------------------------------------
_AI_ML_INFRA: list[Skill] = [
    {
        "id": "embeddings",
        "name": "Embeddings",
        "category": "AI/ML Infrastructure",
        "description": "Dense vector representations of text (or images) that "
        "place semantically similar items near each other in vector space — the foundation of semantic search and RAG.",
        "level": "intermediate",
        "estimated_weeks": 2,
        "prerequisites": ["nlp"],
        "leads_to": ["vector-databases", "rag-systems"],
        "use_cases": ["Semantic search", "Recommendation systems", "Clustering/deduplication of text"],
        "resources": ["sentence-transformers official docs (free, this project uses it)"],
        "job_relevance": "A core building block in essentially every modern search or RAG job posting.",
    },
    {
        "id": "vector-databases",
        "name": "Vector Databases",
        "category": "AI/ML Infrastructure",
        "description": "Databases purpose-built to store embeddings and perform "
        "fast approximate nearest-neighbor search over them at scale — the retrieval half of RAG.",
        "level": "intermediate",
        "estimated_weeks": 2,
        "prerequisites": ["embeddings"],
        "leads_to": ["rag-systems"],
        "use_cases": ["Semantic search backends", "RAG retrieval layers", "Image similarity search"],
        "resources": ["Official ChromaDB docs (free, this project uses it)"],
        "job_relevance": "Explicitly named in most AI-engineering job postings involving search or RAG.",
    },
    {
        "id": "llm-apis",
        "name": "LLM APIs",
        "category": "AI/ML Infrastructure",
        "description": "Calling hosted large language models (Claude, GPT, etc.) "
        "over an API rather than hosting your own — the fastest path to production-grade generation.",
        "level": "beginner",
        "estimated_weeks": 1,
        "prerequisites": ["prompt-engineering"],
        "leads_to": ["rag-systems"],
        "use_cases": ["Chatbots and assistants", "Content generation", "Summarization pipelines"],
        "resources": ["Official Anthropic API docs (free tier/credits)"],
        "job_relevance": "A baseline, near-universal skill in any AI-product engineering role today.",
    },
    {
        "id": "mlops",
        "name": "MLOps",
        "category": "AI/ML Infrastructure",
        "description": "DevOps practices adapted for ML — versioning datasets and "
        "models, automating retraining, and monitoring for model/data drift in production.",
        "level": "advanced",
        "estimated_weeks": 4,
        "prerequisites": ["ci-cd", "machine-learning-fundamentals"],
        "leads_to": ["model-deployment"],
        "use_cases": ["Automated model retraining pipelines", "Production ML monitoring"],
        "resources": ["Google's MLOps whitepaper (free)", "Made With ML free course"],
        "job_relevance": "A distinct, growing job title (\"MLOps Engineer\") at companies running ML in production at scale.",
    },
    {
        "id": "model-deployment",
        "name": "Model Deployment",
        "category": "AI/ML Infrastructure",
        "description": "Packaging and serving a trained model so applications can "
        "call it reliably — covering latency, batching, versioning, and rollback.",
        "level": "advanced",
        "estimated_weeks": 3,
        "prerequisites": ["docker", "machine-learning-fundamentals"],
        "leads_to": [],
        "use_cases": ["Serving custom-trained models via API", "A/B testing model versions in production"],
        "resources": ["Official FastAPI + model-serving tutorials (free)"],
        "job_relevance": "A common responsibility for ML engineers bridging research and production teams.",
    },
]

# ---------------------------------------------------------------------------
# DevOps
# ---------------------------------------------------------------------------
_DEVOPS: list[Skill] = [
    {
        "id": "git-version-control",
        "name": "Git & Version Control",
        "category": "DevOps",
        "description": "The tool nearly every codebase in the world is tracked "
        "with — branching, merging, and collaborating on code changes without stepping on teammates.",
        "level": "beginner",
        "estimated_weeks": 2,
        "prerequisites": [],
        "leads_to": ["ci-cd"],
        "use_cases": ["Collaborating on any codebase", "Tracking changes and reverting mistakes"],
        "resources": ["Official Git documentation (git-scm.com)", "Learn Git Branching (free, interactive)"],
        "job_relevance": "An absolute baseline requirement listed in virtually every engineering job posting.",
    },
    {
        "id": "linux-fundamentals",
        "name": "Linux Fundamentals",
        "category": "DevOps",
        "description": "Command-line proficiency, file permissions, process "
        "management, and shell scripting — the operating system nearly all servers run.",
        "level": "beginner",
        "estimated_weeks": 3,
        "prerequisites": [],
        "leads_to": ["docker", "ci-cd"],
        "use_cases": ["Server administration", "Local development environments", "Debugging deployed services"],
        "resources": ["Linux Journey (free, interactive)", "OverTheWire Bandit (free, hands-on wargame)"],
        "job_relevance": "An implicit requirement for nearly any backend, DevOps, or infrastructure role.",
    },
    {
        "id": "docker",
        "name": "Docker",
        "category": "DevOps",
        "description": "Packages an application with everything it needs to run "
        "into a portable container, eliminating \"works on my machine\" problems across environments.",
        "level": "intermediate",
        "estimated_weeks": 3,
        "prerequisites": ["linux-fundamentals"],
        "leads_to": ["kubernetes", "ci-cd", "microservices"],
        "use_cases": ["Consistent dev/prod environments", "Packaging microservices", "Local multi-service setups"],
        "resources": ["Official Docker Get Started guide (free)"],
        "job_relevance": "One of the most consistently requested DevOps tools across almost all backend job postings.",
    },
    {
        "id": "kubernetes",
        "name": "Kubernetes",
        "category": "DevOps",
        "description": "An orchestration system for running, scaling, and healing "
        "containerized applications automatically across a cluster of machines.",
        "level": "advanced",
        "estimated_weeks": 6,
        "prerequisites": ["docker"],
        "leads_to": ["terraform"],
        "use_cases": ["Running microservices at scale", "Auto-scaling and self-healing deployments"],
        "resources": ["Official Kubernetes docs and tutorials (kubernetes.io)"],
        "job_relevance": "A frequently requested skill in senior backend and dedicated infrastructure/SRE roles.",
    },
    {
        "id": "ci-cd",
        "name": "CI/CD",
        "category": "DevOps",
        "description": "Automating the build, test, and deploy pipeline so every "
        "code change is verified and shipped consistently instead of manually.",
        "level": "intermediate",
        "estimated_weeks": 2,
        "prerequisites": ["git-version-control"],
        "leads_to": ["mlops"],
        "use_cases": ["Automated testing on every pull request", "Automated deployment to production"],
        "resources": ["GitHub Actions official docs (free for public repos)"],
        "job_relevance": "A near-universal expectation; setting up CI/CD is a common signal of production readiness in interviews.",
    },
    {
        "id": "terraform",
        "name": "Terraform",
        "category": "DevOps",
        "description": "Infrastructure-as-code tooling that lets you define cloud "
        "resources in declarative config files instead of clicking through consoles.",
        "level": "advanced",
        "estimated_weeks": 3,
        "prerequisites": ["aws-fundamentals"],
        "leads_to": [],
        "use_cases": ["Reproducible cloud infrastructure", "Multi-environment (staging/prod) parity"],
        "resources": ["Official HashiCorp Terraform tutorials (free)"],
        "job_relevance": "Commonly requested in DevOps/platform engineering and senior backend job postings.",
    },
    {
        "id": "monitoring-observability",
        "name": "Monitoring & Observability",
        "category": "DevOps",
        "description": "Instrumenting systems with logs, metrics, and traces so "
        "you can understand what's actually happening in production before (or while) it breaks.",
        "level": "intermediate",
        "estimated_weeks": 2,
        "prerequisites": ["ci-cd"],
        "leads_to": [],
        "use_cases": ["Debugging production incidents", "Tracking performance/latency regressions"],
        "resources": ["Grafana + Prometheus official free docs/tutorials"],
        "job_relevance": "Regularly listed as a responsibility in backend and SRE job postings.",
    },
]

# ---------------------------------------------------------------------------
# Cloud
# ---------------------------------------------------------------------------
_CLOUD: list[Skill] = [
    {
        "id": "aws-fundamentals",
        "name": "AWS Fundamentals",
        "category": "Cloud",
        "description": "Core services (EC2, S3, RDS, IAM, Lambda) of the largest "
        "cloud provider — enough to deploy and run a real application in production.",
        "level": "intermediate",
        "estimated_weeks": 4,
        "prerequisites": ["linux-fundamentals"],
        "leads_to": ["terraform", "serverless-computing"],
        "use_cases": ["Hosting production applications", "Managed databases and storage", "Serverless functions"],
        "resources": ["AWS Free Tier + official Cloud Practitioner Essentials (free)"],
        "job_relevance": "The most commonly named cloud provider across backend and DevOps job postings.",
    },
    {
        "id": "gcp-fundamentals",
        "name": "Google Cloud Fundamentals",
        "category": "Cloud",
        "description": "Core Google Cloud services (Compute Engine, Cloud Run, "
        "BigQuery) — a strong alternative to AWS, especially common at data/ML-heavy companies.",
        "level": "intermediate",
        "estimated_weeks": 4,
        "prerequisites": ["linux-fundamentals"],
        "leads_to": [],
        "use_cases": ["Hosting containerized apps (Cloud Run)", "Data warehousing (BigQuery)"],
        "resources": ["Google Cloud Skills Boost free tier courses"],
        "job_relevance": "The second/third most commonly named cloud provider, concentrated in data-heavy companies.",
    },
    {
        "id": "serverless-computing",
        "name": "Serverless Computing",
        "category": "Cloud",
        "description": "Running code (functions) without managing servers at "
        "all — the cloud provider handles scaling and you pay only for actual execution time.",
        "level": "intermediate",
        "estimated_weeks": 2,
        "prerequisites": ["aws-fundamentals"],
        "leads_to": [],
        "use_cases": ["Event-driven backends", "Low-traffic APIs where cost matters", "Scheduled jobs"],
        "resources": ["AWS Lambda official docs and free-tier tutorials"],
        "job_relevance": "Frequently mentioned in modern backend postings, especially at cost-conscious startups.",
    },
]

# ---------------------------------------------------------------------------
# Developer Tools
# ---------------------------------------------------------------------------
_DEV_TOOLS: list[Skill] = [
    {
        "id": "testing-frameworks",
        "name": "Testing Frameworks (pytest / Jest)",
        "category": "Developer Tool",
        "description": "Tools for writing automated tests that catch regressions "
        "before they reach production, instead of relying on manual click-testing.",
        "level": "beginner",
        "estimated_weeks": 2,
        "prerequisites": [],
        "leads_to": ["unit-testing-tdd"],
        "use_cases": ["Automated regression testing", "Verifying API behavior in CI"],
        "resources": ["Official pytest docs", "Official Jest docs"],
        "job_relevance": "A baseline expectation; writing tests is a strong, consistently checked interview/take-home signal.",
    },
    {
        "id": "debugging-tools",
        "name": "Debugging Tools",
        "category": "Developer Tool",
        "description": "Using debuggers, browser devtools, and profilers to find "
        "the root cause of a bug systematically instead of guessing and inserting print statements.",
        "level": "beginner",
        "estimated_weeks": 1,
        "prerequisites": [],
        "leads_to": [],
        "use_cases": ["Diagnosing runtime errors", "Performance profiling"],
        "resources": ["Chrome DevTools official docs", "Python's official pdb docs"],
        "job_relevance": "An implicit skill assessed constantly during technical interviews and pair-programming rounds.",
    },
    {
        "id": "api-testing-postman",
        "name": "API Testing (Postman/Insomnia)",
        "category": "Developer Tool",
        "description": "Tools for manually exercising and scripting HTTP API "
        "requests during development, without needing a frontend built yet.",
        "level": "beginner",
        "estimated_weeks": 1,
        "prerequisites": ["rest-api-design"],
        "leads_to": [],
        "use_cases": ["Manually testing backend endpoints during development", "Documenting API behavior for teammates"],
        "resources": ["Official Postman Learning Center (free)"],
        "job_relevance": "A practical everyday tool assumed as baseline familiarity in most backend roles.",
    },
]

# ---------------------------------------------------------------------------
# Software Engineering
# ---------------------------------------------------------------------------
_SOFTWARE_ENGINEERING: list[Skill] = [
    {
        "id": "data-structures-algorithms",
        "name": "Data Structures & Algorithms",
        "category": "Software Engineering",
        "description": "The fundamental building blocks (arrays, trees, graphs, "
        "hash maps) and techniques (sorting, searching, recursion) that underlie efficient software — and most technical interviews.",
        "level": "intermediate",
        "estimated_weeks": 8,
        "prerequisites": ["python"],
        "leads_to": ["system-design"],
        "use_cases": ["Writing efficient code at scale", "Technical interview preparation"],
        "resources": ["NeetCode (free curated problem list + explanations)", "Official Python/Java docs on built-in data structures"],
        "job_relevance": "The dominant focus of technical interviews at most mid-to-large tech companies.",
    },
    {
        "id": "system-design",
        "name": "System Design",
        "category": "Software Engineering",
        "description": "Designing large-scale systems — load balancing, sharding, "
        "caching, consistency tradeoffs — for reliability and scale rather than just correctness.",
        "level": "advanced",
        "estimated_weeks": 6,
        "prerequisites": ["data-structures-algorithms", "database-design"],
        "leads_to": ["distributed-systems"],
        "use_cases": ["Designing scalable backend architectures", "Senior-level technical interviews"],
        "resources": ["System Design Primer (free, GitHub, extremely thorough)"],
        "job_relevance": "The primary interview focus for mid-to-senior backend and full-stack roles.",
    },
    {
        "id": "design-patterns",
        "name": "Design Patterns",
        "category": "Software Engineering",
        "description": "Reusable, named solutions to common software design "
        "problems (Factory, Observer, Strategy) that give engineers a shared vocabulary for structure.",
        "level": "intermediate",
        "estimated_weeks": 3,
        "prerequisites": [],
        "leads_to": [],
        "use_cases": ["Structuring large codebases maintainably", "Communicating architecture decisions with a team"],
        "resources": ["Refactoring.Guru (free, excellent visual explanations)"],
        "job_relevance": "Commonly discussed in code review and design-focused interview rounds.",
    },
    {
        "id": "unit-testing-tdd",
        "name": "Unit Testing & TDD",
        "category": "Software Engineering",
        "description": "Writing small, isolated tests for individual units of "
        "code, and optionally writing those tests before the implementation (test-driven development).",
        "level": "intermediate",
        "estimated_weeks": 2,
        "prerequisites": ["testing-frameworks"],
        "leads_to": [],
        "use_cases": ["Preventing regressions in core business logic", "Documenting expected behavior via tests"],
        "resources": ["Official pytest docs on fixtures/mocking"],
        "job_relevance": "A frequently assessed practice in take-home assignments and code review discussions.",
    },
    {
        "id": "code-review-practices",
        "name": "Code Review Practices",
        "category": "Software Engineering",
        "description": "Giving and receiving constructive, specific feedback on "
        "pull requests — a skill distinct from writing code, but just as important on a real team.",
        "level": "beginner",
        "estimated_weeks": 1,
        "prerequisites": ["git-version-control"],
        "leads_to": [],
        "use_cases": ["Team collaboration on shared codebases", "Mentoring junior engineers"],
        "resources": ["Google's Engineering Practices: Code Review docs (free)"],
        "job_relevance": "An explicit soft-skill component evaluated in most collaborative/team-fit interview rounds.",
    },
    {
        "id": "agile-scrum",
        "name": "Agile & Scrum",
        "category": "Software Engineering",
        "description": "A framework for iterative delivery — sprints, standups, "
        "retros — used by most software teams to organize work and manage scope.",
        "level": "beginner",
        "estimated_weeks": 1,
        "prerequisites": [],
        "leads_to": [],
        "use_cases": ["Coordinating team delivery in sprints", "Managing and prioritizing a backlog"],
        "resources": ["Official Scrum Guide (scrumguides.org, free)"],
        "job_relevance": "Referenced in most job postings as \"experience working in Agile/Scrum environments.\"",
    },
]

# ---------------------------------------------------------------------------
# Computer Science
# ---------------------------------------------------------------------------
_COMPUTER_SCIENCE: list[Skill] = [
    {
        "id": "computer-networking",
        "name": "Computer Networking",
        "category": "Computer Science",
        "description": "How data actually moves between machines — TCP/IP, DNS, "
        "HTTP, TLS — the plumbing underneath every API call and web request.",
        "level": "intermediate",
        "estimated_weeks": 4,
        "prerequisites": [],
        "leads_to": ["rest-api-design", "distributed-systems"],
        "use_cases": ["Debugging connectivity/latency issues", "Designing APIs and network-facing services"],
        "resources": ["Official Cloudflare Learning Center (free, very clear networking explainers)"],
        "job_relevance": "Foundational knowledge frequently probed in backend and infrastructure interviews.",
    },
    {
        "id": "operating-systems",
        "name": "Operating Systems",
        "category": "Computer Science",
        "description": "How processes, memory, and file systems actually work "
        "underneath every program — concurrency, scheduling, virtual memory.",
        "level": "advanced",
        "estimated_weeks": 6,
        "prerequisites": ["cpp"],
        "leads_to": ["distributed-systems"],
        "use_cases": ["Understanding performance and concurrency bugs", "Low-level systems programming"],
        "resources": ["OSTEP — Operating Systems: Three Easy Pieces (free textbook online)"],
        "job_relevance": "A common CS-fundamentals interview topic, especially at larger tech companies.",
    },
    {
        "id": "distributed-systems",
        "name": "Distributed Systems",
        "category": "Computer Science",
        "description": "The theory and practice of systems spanning multiple "
        "machines — consensus, consistency models, failure handling — where the network itself is unreliable.",
        "level": "advanced",
        "estimated_weeks": 6,
        "prerequisites": ["computer-networking", "system-design"],
        "leads_to": [],
        "use_cases": ["Designing fault-tolerant multi-node systems", "Understanding consistency tradeoffs in databases"],
        "resources": ["MIT 6.824 Distributed Systems (free lecture notes/videos)"],
        "job_relevance": "A hallmark topic in senior/staff-level system-design interviews.",
    },
]

# ---------------------------------------------------------------------------
# Combined export
# ---------------------------------------------------------------------------
SKILLS: list[Skill] = (
    _PROGRAMMING_LANGUAGES
    + _FRONTEND
    + _FULL_STACK
    + _BACKEND
    + _DATABASE
    + _AI_ML
    + _AI_ML_INFRA
    + _DEVOPS
    + _CLOUD
    + _DEV_TOOLS
    + _SOFTWARE_ENGINEERING
    + _COMPUTER_SCIENCE
)


def validate_skills(skills: list[Skill]) -> None:
    """Raise ValueError if any skill has a duplicate id or a dangling
    prerequisite/leads_to reference.

    WHY: prerequisites/leads_to are plain id strings, not real foreign keys,
    so nothing enforces referential integrity at write time. This check runs
    once at import time to catch typos immediately instead of silently
    breaking the Step 10 dependency-graph UI later.
    ALTERNATIVE: a real graph database would enforce this automatically, but
    that's the kind of infrastructure this project deliberately avoids for
    50-ish static rows.
    """
    ids = {skill["id"] for skill in skills}
    if len(ids) != len(skills):
        seen: set[str] = set()
        duplicates = set()
        for skill in skills:
            if skill["id"] in seen:
                duplicates.add(skill["id"])
            seen.add(skill["id"])
        raise ValueError(f"Duplicate skill ids found: {duplicates}")

    for skill in skills:
        for ref_field in ("prerequisites", "leads_to"):
            for ref_id in skill[ref_field]:
                if ref_id not in ids:
                    raise ValueError(
                        f"Skill '{skill['id']}' has a {ref_field} reference "
                        f"to unknown skill id '{ref_id}'"
                    )


validate_skills(SKILLS)

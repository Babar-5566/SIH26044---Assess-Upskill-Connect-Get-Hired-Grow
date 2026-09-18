# 🎓 SkillBridge AI — Academia-to-Industry Employability Platform

> An enterprise-grade employability ecosystem bridging higher education and industry hiring through role-based learning tracks, employment outcome analytics, **Multi-LLM Arena intelligence**, and **Grounded Document RAG** with verifiable citations.

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_18_%2B_Vite-61DAFB?style=flat&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript-3178C6?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Language-Python_3.11+-3776AB?style=flat&logo=python)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL_16-4169E1?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind_CSS-38B2D8?style=flat&logo=tailwind-css)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Executive Summary

**SkillBridge AI** is an intelligent employability and skills acceleration platform built for students, academic institutions, mentors, and corporate recruiters. It unifies academic curricula with real-world industry demands, tracking student competencies, automated portfolio readiness, internship lifecycles, and employment outcomes.

Powered by a modern **Enterprise Multi-LLM & RAG Assistant**, SkillBridge empowers users to query internal placement documents, compare competitive reasoning across **OpenAI GPT-4o**, **Anthropic Claude 3.5 Sonnet**, and **Google Gemini 1.5/2.5/3 Flash** simultaneously, and ingest corporate handbooks with strict **anti-hallucination grounding** and **clickable citations**.

---

## 🏗️ Architecture & Data Flow

```mermaid
flowchart TD
    subgraph Client ["Client Layer (React + Vite + TypeScript)"]
        UI["Tailwind CSS + Lucide UI"]
        Arena["Multi-LLM Arena"]
        Chat["Continuous Multi-Turn Chat"]
        RAGUI["Document Ingestion & RAG"]
        Modal["In-App Animated Modals"]
    end

    subgraph Gateway ["API Gateway (FastAPI 0.115+)"]
        AuthGuard["JWT Auth & RBAC Guard"]
        Router["/api/v1 Endpoints"]
    end

    subgraph Core ["Application Core & Services"]
        StudentSvc["Student Lifecycle Service"]
        OutcomeSvc["Employment Outcomes Tracker"]
        RecSvc["Recommendation Engine"]
        MultiLLM["Multi-LLM Async Dispatcher"]
        RAGEngine["Adaptive RAG Pipeline"]
    end

    subgraph AIProviders ["External AI Providers"]
        Gemini["Google Gemini API"]
        OpenAI["OpenAI GPT-4o API"]
        Claude["Anthropic Claude API"]
        OpenRouter["OpenRouter Fallback"]
    end

    subgraph Storage ["Persistence Layer"]
        PG[("PostgreSQL 16\n(Users, Profiles, Outcomes, Logs)")]
        VectorStore[("NumPy Vector Store\n(Cosine Similarity Embeddings)")]
        DocRepo[("Binary Document Storage\n(PostgreSQL BYTEA + Disk Cache)")]
    end

    UI --> Router
    Arena --> Router
    Chat --> Router
    RAGUI --> Router
    Modal --> Router

    Router --> AuthGuard
    AuthGuard --> StudentSvc & OutcomeSvc & RecSvc & MultiLLM & RAGEngine

    MultiLLM -->|asyncio.gather| Gemini & OpenAI & Claude & OpenRouter
    RAGEngine -->|Dense Embeddings| VectorStore
    RAGEngine -->|Context Synthesis| Gemini
    StudentSvc & OutcomeSvc & RecSvc --> PG
    RAGUI --> DocRepo
```

---

## 🚀 Key Modules & Completed Phases

### 1. Phase 8: Robust Backend Foundation
- **FastAPI Core**: Modular architecture with versioned routing (`/api/v1`).
- **PostgreSQL 16 & SQLAlchemy 2.x**: Relational schema modeling with Alembic migration history.
- **Authentication & RBAC**: Stateless JWT bearer tokens, bcrypt password hashing, and role hierarchies (`STUDENT`, `ADMIN`, `INDUSTRY_ADMIN`, `FACULTY`, `MENTOR`, `RECRUITER`).
- **Standardized Response Envelope**: Uniform `{ success, data, error }` contract.

### 2. Phase 9: Student Portfolio & Lifecycle
- Comprehensive profile completeness scoring and real-time skill proficiency tracking.
- Project showcases, certifications, achievements, and internship experience logs.
- Direct-to-database resume storage (`BYTEA`/`LargeBinary`) preserving security and data isolation.

### 3. Phase 21: Employment Outcome Tracking
- Auditable tracking of employment transitions: company, job title, salary/CTC, offer letters, joining dates, and employment types.
- RESTful CRUD with student ownership verification.

### 4. Phase 22 & 23: Resilient AI Recommendation Engine
- Dual-tier failover: `Gemini Primary -> OpenRouter Fallback -> Deterministic Rule-Based Fallback`.
- Telemetry log table (`ai_executions`) storing latency, token counts, error codes, and outputs.
- Normalized career, learning path, and internship recommendations.

### 5. Phase 24: Enterprise Multi-LLM + Grounded RAG Assistant
- 🥊 **Multi-LLM Arena**:
  - Concurrent side-by-side prompt dispatch across **OpenAI (gpt-4o)**, **Anthropic Claude (claude-3-5-sonnet)**, and **Google Gemini (gemini-3-flash-preview)** via `asyncio.gather`.
  - Live latency benchmarking, token metrics, and visual comparison grids.
- 💬 **Continuous Multi-Turn AI Chat**:
  - Conversational context-aware workspace with seamless model switching and clear chat history management.
- 📚 **Grounded Document RAG with Verifiable Citations**:
  - Multi-format ingestion: **PDF**, **DOCX**, and **TXT** files (up to 25MB).
  - Semantic recursive chunker with overlap and page-number preservation.
  - **Adaptive Thresholding Retrieval**: Dynamic cosine similarity scoring (0.48/0.45 fallback) ensuring 100% recall for scoped document queries.
  - **Strict Anti-Hallucination Grounding**: Deterministic refusal (*"I could not find sufficient information in the uploaded documents to answer this question."*) when relevant context is absent.
  - **Clickable Interactive Citations**: Footnote badges `[1]`, `[2]` linking directly to document names, page indices, and verbatim snippet previews.
- 🎨 **Custom In-App Animated Delete Modal**:
  - Replaced browser `window.confirm()` with an animated dialog.
  - Features dark backdrop blur (`backdrop-blur-xs`), smooth entrance zoom animation (`zoom-in-95 duration-200`), file metadata badge, permanent vector purge alert, and responsive delete/cancel controls.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite 6, TypeScript, Tailwind CSS, Lucide Icons, Axios |
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, Pydantic Settings |
| **Database & ORM** | PostgreSQL 16, SQLAlchemy 2.x, Alembic, psycopg |
| **Authentication** | JWT (python-jose), Passlib (bcrypt) |
| **Vector Engine & RAG** | NumPy Cosine Similarity, PyPDF, python-docx, In-Memory/Disk Vector Persistence |
| **LLM Integrations** | Google Gemini API, OpenAI API, Anthropic Claude API, OpenRouter |
| **Testing & Verification** | Pytest, HTTPX, Playwright MCP End-to-End Automation |

---

## ⚡ Quick Start Guide

### Prerequisites
- **Node.js**: `v18.x` or higher
- **Python**: `3.11` or higher
- **PostgreSQL**: `v16` running locally or accessible remotely

---

### 1. Backend Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Babar-5566/SIH26044---Assess-Upskill-Connect-Get-Hired-Grow.git
   cd SIH26044---Assess-Upskill-Connect-Get-Hired-Grow/backend
   ```

2. **Create and activate virtual environment**:
   ```powershell
   # Windows (PowerShell)
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```

   Ensure the following keys are populated in `backend/.env`:
   ```env
   DATABASE_URL=postgresql+psycopg://skillbridge:skillbridge@localhost:5432/skillbridge
   TEST_DATABASE_URL=postgresql+psycopg://skillbridge:skillbridge@localhost:5432/skillbridge_test
   SECRET_KEY=your-super-secret-jwt-key
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000

   # AI Provider Keys
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini-2.5-flash
   OPENAI_API_KEY=your_openai_api_key
   CLAUDE_API_KEY=your_claude_api_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   AI_TIMEOUT_SECONDS=40
   ```

5. **Run Migrations & Seed Data**:
   ```bash
   alembic upgrade head
   python -m app.scripts.seed
   ```

6. **Start Backend Server**:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   - API Docs (Swagger): `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

---

### 2. Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd ../frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start Development Server**:
   ```bash
   npm run dev
   ```
   - App URL: `http://localhost:5173`

---

## 👥 Demo Credentials

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Student** | `student.test@gmail.com` | `student@123` | Profile, RAG Assistant, Skills, Applications, Outcomes |
| **Admin** | `admin.test@example.com` | `admin@123` | Full administrative oversight and user management |
| **Recruiter** | `recruiter.test@example.com` | `recruiter@123` | Job/Internship postings, candidate search |
| **Faculty** | `faculty.test@example.com` | `faculty@123` | Academic performance reviews, curriculum tracks |
| **Mentor** | `mentor.test@example.com` | `mentor@123` | 1-on-1 student mentorship, mock interviews |
| **Industry Admin** | `industry.admin.test@example.com` | `industry@123` | Corporate partnership and placement analytics |

---

## 📡 API Endpoints Reference

### Authentication (`/api/v1/auth`)
- `POST /register` — Register a new student or corporate account
- `POST /login` — Authenticate and receive a signed JWT bearer token
- `GET /me` — Fetch current user context and permissions

### Student Lifecycle & Outcomes (`/api/v1/students`)
- `GET /me` — Full student profile with completeness calculation
- `GET /me/skills` | `POST /me/skills` — Manage technical & professional skills
- `GET /me/resume` | `POST /me/resume` — Secure binary resume upload & download
- `GET /me/outcomes` | `POST /me/outcomes` — Track salary, offers, and placement data

### Multi-LLM & Grounded RAG Assistant (`/api/v1/ai-assistant`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/models` | List active foundation models (Gemini, Claude, GPT-4o) with status |
| `POST` | `/compare` | Dispatches identical prompt concurrently across all configured LLMs |
| `POST` | `/chat` | Continuous conversational multi-turn chat with persistent context |
| `POST` | `/documents/upload` | Ingests PDF/DOCX/TXT, extracts text, generates vector chunks & index |
| `GET` | `/documents` | Lists all indexed vector documents and chunk counts for current user |
| `DELETE` | `/documents/{id}` | Purges document from disk and removes all vectors from index |
| `POST` | `/rag/query` | Adaptive vector search + Grounded synthesis with citations `[1]`, `[2]` |

---

## 🧪 Testing & Quality Verification

### Automated Backend Tests
Run the comprehensive pytest suite:
```bash
pytest backend/tests -v
```

**Test Coverage Highlights**:
- `test_ai_assistant_api.py`: Upload, query lifecycle, fallback handling, delete cascade.
- `test_rag_engine.py`: Scoped retrieval, adaptive thresholding, anti-hallucination refusal.
- `test_vector_store.py`: Vector normalization, cosine similarity top-K ranking, persistence.
- `test_rag_ingestion.py`: PyPDF, python-docx, plain TXT chunking with overlap guarantees.
- `test_multi_llm_adapters.py`: Independent adapter response formatting and error handling.
- `test_security_audit.py`: Role boundaries, unauthorized token rejections.

```text
============================= 20 passed in 22.46s =============================
```

### Automated End-to-End Verification
Visual workflows and UI states are verified using **Playwright MCP**:
- In-App animated delete confirmation modal verified with zero native browser alerts.
- Clickable citation cards open snippet inspector modals with metadata.
- 1-Click Re-Analysis triggers adaptive scoped retrieval with 100% chunk recall.

---

## 🔒 Security & Privacy

- **Server-Side AI Secrets**: API keys for OpenAI, Anthropic, and Google Gemini are never leaked to client bundles or browser localStorage.
- **Tenant Document Isolation**: Document ingestion and RAG vector searches are partitioned per authenticated user; cross-tenant document exposure is rejected at the vector query filter.
- **Strict Anti-Hallucination**: If semantic similarity falls below threshold, the AI explicitly states insufficient context rather than hallucinating facts.
- **Cryptographic Security**: Passwords hashed using bcrypt; JWT tokens validated with expiration boundaries and subject checks.

---

## 📄 License

This project is licensed under the **MIT License**.

- Full license text: [LICENSE](LICENSE)
- You are free to use, modify, distribute, and integrate this software into commercial or academic projects, provided the original copyright notice and warranty disclaimer are preserved.


# Frontend

React, TypeScript, and Vite. Use Node.js 22.12 or newer.

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. Run the FastAPI backend on `127.0.0.1:8000`.
The default API base is `/api/v1`; Vite proxies requests to the backend. The
same relative URL works with the nginx deployment proxy. On initial setup,
copy `.env.example` to `.env`; preserve an existing environment file.

The AI workspace includes model comparison, separate in-session model histories,
Markdown answers, file upload by browsing or drag-and-drop, searchable documents,
and citations with source-text dialogs. Server connection, document loading, and
upload failures have separate status messages and retry controls.

```powershell
npm run build
npm run test:e2e
```

Browser tests mock provider responses and document operations, so they do not
incur AI usage or change real documents. The assistant and Markdown renderer load
only when the AI workspace is opened.

If the document library fails while the server is connected, run
`python -m alembic upgrade head` from `backend/`. In particular, revision
`0012_rag_documents` creates the document metadata table.

# Multi-LLM and RAG audit — 19 September 2026

## Follow-up: reported Network Error and frontend polish

The live server was reachable, but the database was still at revision
`0011_notification_delivery` and had no `rag_documents` table. The document-list
request returned HTTP 500. Because the frontend called the backend origin
directly, that error response lacked a CORS header and appeared as `Network Error`.

During the follow-up, the existing migration was applied to the configured database
(`0012_rag_documents`). The frontend's local and example API base now use `/api/v1`,
and Vite forwards requests to `127.0.0.1:8000`. Authenticated live document listing
and the health endpoint both returned HTTP 200 after the change.

The assistant UI was rebuilt with consistent model cards, Markdown answers, copy
controls, in-session model histories, drag-and-drop upload, document selection and
search, source previews, focus-managed dialogs, independent error/retry states,
and responsive layouts. The assistant route is loaded on demand.

Validation: production build passed; 12 Chromium browser tests passed. Upload,
provider generation, and document deletion in the browser suite use fixtures;
live paid LLM/embedding calls were not made. Desktop and mobile source displays
were also visually inspected.

The sections below describe the earlier audit before this follow-up.

The existing app was reviewed against the supplied Enterprise Multi-LLM + RAG
requirements. This audit fixes the implemented module; it does not add every
feature in the original staged roadmap or certify production readiness.

## Confirmed defects and fixes

| Finding | Correction |
| --- | --- |
| Anonymous callers could invoke paid AI routes, read document metadata/content, and delete other users' documents. Invalid tokens silently became anonymous. | Reuse existing authentication on every AI route; require document ownership before read, query, and deletion; remove unscoped fallback listings. |
| Upload reported success after a database error, leaving untracked vectors/files. The RAG table was missing from migrations. | Add revision `0012_rag_documents`, flush metadata before indexing, and undo a failed upload's index/file writes. |
| Reads loaded the entire upload before enforcing its size limit. | Bound upload reads, store originals under UUID filenames, reject binary TXT and oversized expanded DOCX files, and return safe parsing errors. |
| Large paragraphs were not recursively split, so one chunk could exceed the configured limit. TXT/DOCX citations invented a page 1. | Enforce the chunk ceiling with overlap; retain real PDF pages and leave unknown page numbers empty. |
| A provider failure silently substituted 256-dimensional hash vectors into a semantic index. Different models and dimensions could be mixed. | Stop provider failures with a clear error; validate counts, finite values, dimensions, and embedding model identity. Keep no-key hashing as demo/test mode only. |
| Vector files could be written out of sync; failed persistence left mutated memory. | Save metadata and vectors together in an atomic NumPy snapshot, restoring memory on failed writes. |
| Explicit relevance thresholds were relaxed or a zero threshold was replaced by the default. Responses showed all retrieved chunks even if unused. | Honor explicit thresholds, reject absent/invalid citation IDs, return only cited chunks, and expose complete cited text. Escape context delimiters in retrieved content. |
| Changing chat models shared the same conversation history; editing an arena prompt changed the continuation's original question. | Maintain independent histories per provider and remember the actual compared question. Failed requests are kept out of model history. |
| Frontend ignored the backend error envelope; RAG errors could display an empty answer. Mobile sidebar/layout overflowed. | Display inline errors, upload progress, and responsive navigation. Test all three tabs at a 390 px viewport. |
| Example secret variable was ignored, comma-separated CORS settings could fail to parse, and browser tests required Edge although CI installs Chromium. | Support documented/legacy configuration names, parse CORS formats, protect production configuration, and use the installed Chromium runner. |
| Existing tests could consume live API credentials and write to the user's RAG directories. | Isolate test storage and disable provider credentials before importing the application. |

## Verification

- Initial frontend build: passed, with a non-blocking dynamic import warning.
- Initial backend suite: 68 passed. Those tests did not cover the defects above.
- Revised backend suite: 109 passed, including authenticated lifecycle and ownership,
  upload rollback, PDF text/page extraction, DOCX/TXT extraction, bounded chunking,
  embedding failures, index compatibility/persistence, explicit thresholds,
  citations, input validation, and concurrent provider failure isolation.
- Chromium browser suite: 8 passed, including model history isolation, prompt
  continuation, failed-message retry, upload/RAG errors, and mobile layout.
- Production frontend build: passed. Removed the ineffective dynamic import that
  caused the initial Vite warning.
- Frontend dependency audit: npm reported zero vulnerabilities.
- New migration: upgrade and repeated upgrade exercised against a temporary SQLite
  database. PostgreSQL migration SQL is also generated offline.

Run from the repository root:

```powershell
Set-Location backend
python -m pytest -q
Set-Location ../frontend
npm run build
npm run test:e2e
```

## Existing installation

1. Back up the database and RAG storage before upgrading a real deployment.
2. Run `python -m alembic upgrade head` **from `backend/`**. This adds the missing
   document metadata table; it does not assign owners to previously anonymous data.
3. Sign in before using AI routes. Anonymous or inactive accounts cannot access them.
4. Existing indexes without embedding identity cannot be reliably matched to a
   model. Preserve the old files, select a new `RAG_VECTORS_DIR`, restart the app,
   and re-upload the original documents under the correct user. This audit does
   not erase, migrate, or re-embed the user's existing documents automatically.
5. Configure provider keys using `backend/.env.example`. Keep the embedding model
   fixed for an index; a provider outage now returns an error instead of changing it.

## Remaining limits

- Provider responses are mocked in automated tests. Live OpenAI, Claude, Gemini,
  quotas, and configured model availability have not been verified.
- The user's PostgreSQL database has not been changed. A complete fresh PostgreSQL
  installation and Docker/cloud deployment were not exercised in this audit.
- RAG prompting and citation-ID validation cannot guarantee factual grounding of
  every claim. Important answers still need source review and representative
  retrieval/grounding evaluations. Top-K summaries do not cover every chunk.
- NumPy storage is suitable for one worker. Multi-process writes, database/index
  crash recovery, large-scale ingestion, and resource-isolated parsing need a
  more robust storage/job design before a large production deployment.
- Conversation histories are held in page memory. Saved chats across reloads,
  an assistant settings screen, and durable usage/cost monitoring are still absent.
- Legacy unowned documents are deliberately excluded from private searches. An
  administrator must explicitly establish ownership before exposing old data.

OpenAI embedding dimensionality and cosine similarity were checked against the
[official embeddings guide](https://developers.openai.com/api/docs/guides/embeddings).

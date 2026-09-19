# Profile AI

Open **Multi-LLM & RAG AI → My Profile AI**, or `/ai-assistant?tab=profile`, in a student account.

## What is implemented

- The current saved profile resume is analyzed automatically. Existing resumes are queued by the migration; new uploads enqueue extraction in the same transaction as the file.
- The workspace combines education, skills, projects, certifications, internships, achievements, saved links, and the active resume.
- Skills have separate profile and resume provenance. Resume suggestions only enter the profile when the student reviews and saves them as self-reported skills.
- Three-line profile and improvement summaries work without API keys.
- PDF/DOCX text, sections, visible URLs and embedded hyperlink targets are extracted. Text chunks retain actual PDF page numbers; DOCX pages are unknown.
- A text-based resume quality checklist and explicit job skill coverage replace unexplained ATS percentages. Profile evidence never inflates submitted-resume coverage.
- Matching uses an open job posting or a pasted JD. Detected JD skill mentions are labeled unconfirmed; students can supply a reviewed required-skills list.
- Subject and learning links are available directly in the overview, matched to saved skills, recognized resume skills, project technologies and field of study. They come from the existing resource catalog, restricted to public resources and the active organization. Ready study documents can open a scoped conversation directly from this card.
- Job matching also suggests catalog resources for gaps and clearly labeled practice projects.
- Chat supports profile/resume with skill learning, resume only, one saved project with an optional supporting document, uploaded documents, and target-job scopes.
- Profile and project conversations distinguish personal evidence, recorded-topic learning, clarification and unrelated requests. General learning answers have a visible label and no resume citations.
- All three model adapters receive the same selected evidence or learning context. Invalid citations or non-verbatim supporting quotes produce a retryable evidence-answer error.
- Complete skill/project lists and the three-line summary use direct facts rather than top-K retrieval. These shortcuts work without an LLM.
- Resume replacement/deletion and profile/source version changes invalidate stale chat and job-match results.

## Leader request coverage

| Requested behavior | Implemented behavior |
| --- | --- |
| Automatically read the resume from the profile | The existing profile upload stores the file and queues background analysis in one transaction. No second upload to Document RAG is required. |
| Identify the user's skills | Read recorded profile skills and recognize supported skill names/aliases in the active resume. Keep provenance separate; adding a suggested skill requires the student's review. |
| Projects and project links | Show saved project records and links, extract visible and embedded resume links, and support questions about a selected project. |
| Subject links and related documents | Show matching catalogue links in **Subject & learning links** without requiring a target job. Select uploaded study notes for document-grounded questions, or attach a supporting document to a project conversation. |
| Talk about the profile and related skills | Cite personal evidence. Label general learning answers separately. Check every new topic and guide unrelated/unclear questions back to the supported scope. |
| Three-line profile/ATS-style feedback | Provide a three-line profile summary, three improvement points, a text-quality checklist and job-specific keyword coverage. No vendor ATS score or hiring probability is invented. |

Links are references: remote website/repository contents are not fetched. Upload the relevant README, report or study notes to discuss their contents. Catalogue links describe recorded resource metadata; the assistant has not read their web pages.

This feature currently uses student account authorization. General job-seeker registration, teacher job-seeker access and automatic discovery of external job postings remain separate proposed work.

## Run locally

Run backend commands from `backend/`, not the legacy root `app/` directory:

```powershell
cd D:\hackathon\SIH26044---Assess-Upskill-Connect-Get-Hired-Grow\backend
python -m alembic upgrade head
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
cd D:\hackathon\SIH26044---Assess-Upskill-Connect-Get-Hired-Grow\frontend
npm install
npm run dev
```

Migration `0013_profile_resume_analysis` creates the durable extraction queue and backfills active saved resumes. The local database was upgraded during implementation.

`PROFILE_ANALYSIS_WORKER_ENABLED=true` enables the in-process queue consumer in the FastAPI lifespan. It polls every three seconds when idle, claims jobs with database row locks, and processes parsing off the event loop. Jobs and results persist in PostgreSQL. A five-minute lease permits interrupted jobs to be reclaimed; three interrupted attempts require an explicit retry. Publication checks both the lease token and active document, so old work cannot replace a newer upload.

There is no extra queue service to start. Keep one backend worker while using the application's existing local RAG vector store. A separate managed worker would be appropriate for high-volume deployment.

`MAX_RESUME_SIZE_MB` defaults to 5; the UI reads this limit from the API. RAG document uploads retain their separate 25 MB default. General generated answers require a configured provider key; extraction, summaries, keyword matching and the three fact shortcuts do not.

## How questions are handled

The default **Profile, resume & learning** scope supports both personal evidence and learning. A selected project's recorded technologies can also support learning.

| Question type | Behavior |
| --- | --- |
| Personal profile, resume or project question | Retrieve owned facts/chunks, generate an answer, then validate citation IDs and exact supporting quotes. |
| Learning question related to a recorded topic | Teach from general model knowledge. Show **Skill learning · topic** and a note explaining that the answer is not resume/document evidence. No source excerpts or source citations accompany this generation. |
| Ambiguous question or learning topic not recorded | Ask the student to identify a recorded topic or save a relevant missing skill. |
| Unrelated request, including a mixture of related and unrelated requests | Give a brief redirect to profile/skills/career topics or Continuous Chat. Do not call the answer-generation model. |
| Routing failure or invalid model classification | Show a retry/model-selection error; do not guess a topic or generate an unrestricted answer. |

For example, a Python resume can support "Who created Python?" and a Java resume can support "Explain Java interfaces." These are general learning answers, not facts retrieved from the resume. A later recipe or live sports-score request is evaluated as a new question. There is no food/sports blacklist: the router considers the actual task and the student's recorded topics.

Eligible topics come from saved profile skills, recognized active-resume skills, department and project technologies. Project scope limits topics to the selected project's technologies. A question or fabricated conversation history cannot add a new eligible topic. Supporting document text does not automatically register a new profile skill.

Complete, unambiguous fact/learning questions have lightweight shortcuts. Other wording uses one structured model classification, with a topic ID checked against the current recorded list (up to 120 topics, prioritizing direct mentions). Comparison mode shares this one decision across all answer models. This can add one provider request before generation; classification is probabilistic, not a guaranteed content filter. The router receives topic names, selected project title and up to four prior user questions, not raw resume excerpts or previous assistant claims.

**Resume only**, **My documents**, **Target job & my evidence**, and the separate **Document RAG & Citations** tab keep their evidence-only behavior. Choose the default profile scope for general learning. Source access is checked before routing; source changes during routing or generation invalidate the response. UI and fixed application messages use English; the model is instructed to understand questions in any language and reply in English.

## API

All paths are under `/api/v1` and require student authorization.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/profile-intelligence` | Current facts, source version, analysis status, summaries, suggestions, matched catalogue links and owned document metadata |
| POST | `/profile-intelligence/refresh` | Queue explicit resume re-analysis; returns 202 |
| GET | `/profile-intelligence/jobs` | Up to 100 open job postings |
| POST | `/profile-intelligence/job-match` | Body: either `job_id`, or `job_description` and optional `required_skills` |
| POST | `/profile-intelligence/chat` | Body: `question`, `provider`, `scope`, optional source IDs/target, `compare`, `version`, bounded history |
| POST | `/students/me/resume` | Existing upload route, now atomically queues extraction |
| DELETE | `/students/me/resume` | Deletes this student's saved resumes and extraction artifacts |

JSON bodies carry JD/question text; personal content is not placed in URL parameters. Source IDs are checked against the authenticated owner before retrieval. History is conversation context, not evidence. No raw resumes or chat prompts are added to execution logs by this feature.

Each chat answer includes `answer_kind` (`profile`, `skill_learning`, `clarification`, `out_of_scope` or `conversation`), with `topic` and `knowledge_note` for learning. Learning responses always return an empty `sources` list; malformed output or numbered prose citations produce a retryable error. Code examples can still use array indexing.

The legacy `/resume-intelligence/analyze` endpoint is unchanged; the new UI uses the APIs above for saved-resume analysis and matching.

## Retrieval and limits

Resume analysis uses a conservative skill vocabulary, aliases and explicit evidence matching, not a paid generative extraction call. Skills not recognized by the catalog can be added by the student; their exact resume evidence is checked against cached chunks without re-parsing. Listed skills do not establish proficiency. Negation detection is conservative and does not understand every possible phrasing.

Profile chat uses live database facts and bounded lexical retrieval over resume chunks and the user's existing RAG document chunks. General Document RAG continues using its existing embedding pipeline. Profile AI does not duplicate the saved resume into that vector store or incur embedding charges.

External websites, GitHub repositories and private links are **not fetched**. Upload relevant README/design documents and select them as supporting evidence. OCR and old binary DOC conversion are not included. Unreadable files show actionable feedback. Partially readable PDFs report incomplete extraction; unmatched requirements remain unknown instead of receiving a fabricated missing-skill score.

The checklist checks extracted text, not every layout feature or vendor ATS rule. Keyword coverage does not evaluate full job eligibility, years of experience or hiring likelihood. A quote/citation validator verifies source membership and literal quotations; it cannot prove that every generated claim is semantically supported. Review consequential advice against the shown sources.

Chat history is kept only in the current page session and cleared when its scope/model/source version changes. Replaced resume bytes remain in the existing versioned document storage until the student uses Delete resume; only the active resume is eligible for retrieval.

## Verification

```powershell
# backend/
python -m pytest -q

# frontend/
npm run build
npm run test:e2e
```

Tests cover real DOCX parsing, upload/queue/analysis lifecycle, resume replacement/deletion, interrupted-job recovery, late-worker publication, profile/resume separation, skill aliases and URL exclusions, custom skills, partial/scanned PDFs, embedded links, explicit job requirements, catalog visibility, complete skill lists, cross-user project/document access, source changes during generation, citation rejection and identical multi-model context.

Routing tests also cover multiple resume topics, switching from Python to Node.js and back in the same conversation, Node.js/NodeJS/Node JS spellings, short follow-ups, unrelated new subjects, mixed requests, invalid classifier output, provider failure, unrecorded topics, selected-project isolation, fabricated learning citations, code indexing and source changes during classification. Catalogue tests cover resume/profile/project/department matches, URL validation and organization visibility without a target job. Mocked model outputs verify application behavior; they do not measure a live classifier's accuracy. The backend suite passed all 182 tests.

All 21 Chromium tests passed. They cover the workspace, reviewed skill additions, automatic status polling, job-match evidence, selected project/doc scopes, model switching, deletion confirmation, error retry, mobile layout, learning labels, an unrelated follow-up, switching back to evidence-only answers, subject links and directly opening a study-document conversation. The frontend production build passed; the running database is at migration `0013_profile_resume_analysis`.

A temporary fixture profile was also exercised against the running backend and PostgreSQL: real upload → background READY → fact chat → job match → deletion. The fixture was removed. LLM responses are mocked in automated tests; those tests do not make paid provider or embedding requests.

A separate live smoke check used `gemini-3-flash-preview` with a synthetic DOCX containing Python and Node JS. Python's creator and then the Node.js event loop both produced validated learning answers with no citations. Subsequent paneer-recipe and live-cricket-score questions both routed to the scope guide. All four checks passed. This small check confirms these examples, not perfect classification for every phrasing. No real student data or embedding calls were used.

A subsequent audit exercised the actual HTTP API and PostgreSQL with a temporary student account: saved-resume upload → background READY → skill extraction → three fact shortcuts → separate profile/resume job coverage → Gemini profile/project answers with verified quotations → recorded-skill learning → unrelated follow-up → TXT ingestion → study-document and project-supporting-document citations → embedding-based Document RAG → parallel model comparison. All 18 recorded checks, including completion and cleanup, passed. This audit made live model and document-embedding requests using synthetic content. The temporary user, resume and uploaded RAG document were removed; a follow-up database check found no remaining audit users.

Provider availability is separate from application test results. In the live comparison, Gemini returned an answer while OpenAI and Claude returned isolated errors. A direct OpenAI check reported **Invalid OpenAI API key**; Claude has no configured key. All three adapters are implemented and tested, but obtaining answers from all three providers requires working credentials for each. No keys were changed or printed during the audit.

If an older analysis missed the spelling "Node JS", use **Retry resume analysis** once to apply the expanded alias recognition to that saved file.

The prompting boundary follows the [official OpenAI guidance on untrusted input](https://developers.openai.com/api/docs/guides/agent-builder-safety): source data stays in the user context, while policy instructions remain static. The local review-agent skill was used for the final defect review.

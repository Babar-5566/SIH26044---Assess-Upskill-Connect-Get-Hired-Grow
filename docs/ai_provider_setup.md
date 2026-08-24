# Gemini and OpenRouter Setup

Gemini is the primary provider. OpenRouter is the fallback provider. Both are optional; if neither key is configured, recommendation generation uses deterministic rule-based fallback.

## Environment

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key
GEMINI_MODEL=gemini-2.5-flash
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_MODEL=openai/gpt-4o-mini
AI_TIMEOUT_SECONDS=20
AI_MAX_RETRIES=2
```

The backend calls providers only. API keys must never be sent to the frontend or committed to Git.

## Flow

1. The router collects only the authenticated student's relevant profile context.
2. `AIExecution` is created as `PENDING`.
3. Gemini is tried first.
4. OpenRouter is tried if Gemini is unavailable or fails.
5. Every provider is retried according to `AI_MAX_RETRIES`.
6. Valid JSON is required from the provider.
7. Valid recommendation items are saved to `recommendations`.
8. If all providers fail, deterministic rule-based recommendations are returned.

## Endpoint

```text
POST /api/v1/students/me/recommendations/generate
```

The endpoint never exposes provider API keys. Provider errors are stored in `ai_executions` and the user still receives a usable fallback response.

## Design Boundary

Authentication, authorization, profile completeness, ownership, eligibility, and fixed scoring remain deterministic. AI is used for explanation and optional recommendation generation only.

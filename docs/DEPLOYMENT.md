# Production Deployment

Set `POSTGRES_PASSWORD`, `SECRET_KEY`, `GEMINI_API_KEY`, and `OPENROUTER_API_KEY` in an external secret manager. Never commit `.env` files.

Run `docker compose up --build` from the repository root. The backend container applies Alembic migrations before starting; the frontend is served by nginx.

For multiple backend workers, put rate-limit and token-revocation state in shared Redis, terminate TLS at the ingress, enable database backups, and ship structured audit logs to durable storage. Run `npm audit`, backend tests, and Playwright E2E in CI before deployment.

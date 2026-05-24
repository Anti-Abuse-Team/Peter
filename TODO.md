# TODO

- [x] Remove hardcoded OpenRouter API key from `cogs/peter.py`.
- [x] Require `OPENROUTER_API_KEY` from environment only (no fallback key in code).
- [x] Change default AI provider to `ollama` to avoid OpenRouter-key startup issues.
- [x] Improve invalid-key guidance/error messaging for safer setup.
- [x] Add token/key safety checks to avoid exposing secrets in logs or messages.
- [x] Review and provide secure `.env` recommendations.

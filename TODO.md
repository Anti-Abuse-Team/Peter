# AI Provider Upgrade Progress (Add Free Cloud Provider)

## Plan Steps:
- [x] Confirm migration target: add free cloud AI provider while keeping local providers
- [x] Create/update task checklist during implementation
- [ ] Update cogs/peter.py:
  - [ ] Extend provider router to `PETER_AI_PROVIDER=ollama|lmstudio|openrouter`
  - [ ] Add OpenRouter path (`https://openrouter.ai/api/v1`) via OpenAI-compatible client
  - [ ] Add env-driven cloud model selection with free default model
  - [ ] Keep `PETER_CHANNEL` routing behavior unchanged
  - [ ] Keep Peter persona and embed reply behavior
  - [ ] Add provider-specific error handling for cloud failures
- [x] requirements.txt:
  - [x] Keep `openai` (already sufficient for LM Studio + OpenRouter)
  - [x] No extra dependency required
- [ ] User setup in .env:
  - [ ] PETER_AI_PROVIDER=openrouter
  - [ ] OPENROUTER_API_KEY=<your_openrouter_api_key>
  - [ ] OPENROUTER_MODEL=meta-llama/llama-3.1-8b-instruct:free
  - [ ] PETER_CHANNEL=your_channel_id
  - [ ] (optional local fallback) keep OLLAMA_* and LMSTUDIO_* vars
- [ ] Testing:
  - [ ] Start bot and verify cog loads
  - [ ] Verify OpenRouter reply in PETER_CHANNEL
  - [ ] Verify graceful behavior for missing key / invalid model / rate limit
  - [ ] Verify ollama/lmstudio still work if selected

## Status:
In progress.

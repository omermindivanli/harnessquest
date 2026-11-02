# Tutorial 8: Local LLMs with Ollama (Level 10)

```bash
# install from https://ollama.com, then:
ollama serve
ollama pull llama3.1:8b
harnessquest --prompt "List the files" --provider ollama --model llama3.1:8b
```

Why local: free, private, offline, and a great way to see how weaker models stress a harness. Small models forget the `[TASK_COMPLETE]` marker or the `RUN:` format more often, which is exactly why a good harness has clear rules in its prompt, turn limits and loop detection.

**Exercise:** run the same task on a small and a large model and write what differed in `my_harness/ollama_notes.md`.

Troubleshooting: `curl http://localhost:11434/api/tags` should list your models. Set `OLLAMA_BASE_URL` in `.env` for a remote server.

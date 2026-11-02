# Tutorial 7: Multi-Provider and Fallback (Levels 9-11)

The model is a commodity; the harness should not care which one answers.

HarnessQuest hides providers behind `LLMProvider.complete()`. List them with `harnessquest --list-providers`. Use `--provider mock` for offline tests.

**Fallback pattern**

```python
async def complete_with_fallback(providers, messages, model):
    last = None
    for p in providers:
        try:
            return await p.complete(messages=messages, model=model)
        except Exception as e:   # rate limit, outage, bad key
            last = e
    raise last
```

**Exercise** (`my_harness/providers.py`): implement this with a primary and secondary provider and test it by making the primary raise.

Cost tip: route simple turns to a cheap model and hard ones to a strong model.

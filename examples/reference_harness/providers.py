"""Level 9 reference: try providers in order, fall back on failure."""


async def complete_with_fallback(providers, messages, model):
    last_error = None
    for provider in providers:
        try:
            return await provider.complete(messages=messages, model=model)
        except Exception as e:  # rate limit, outage, bad key ...
            last_error = e
    raise last_error if last_error else RuntimeError("no providers configured")

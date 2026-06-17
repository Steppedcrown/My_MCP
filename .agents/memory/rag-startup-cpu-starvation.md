---
name: RAG startup CPU starvation
description: sentence_transformers weight loading in a background thread blocks gunicorn gthread workers from responding, causing healthcheck timeouts on deployment.
---

# RAG startup causes gunicorn healthcheck timeouts

## The rule
When `rag.build_index()` runs in a `threading.Thread` at gunicorn startup, it loads sentence-transformer model weights (CPU-heavy numpy ops). Python's GIL means this starves the gthread HTTP workers, causing every healthcheck to time out even though gunicorn is listening on its port.

**Why:** `gthread` workers share the GIL with background threads. CPU-bound work in a background thread blocks the HTTP threads from making progress.

**How to apply:** At the start of `_build_rag_index()` in `app.py`, call `time.sleep(30)` before doing any model loading. This lets gunicorn pass its initial healthchecks before the CPU load begins. The RAG index becomes available ~30s after boot; the existing `if not _rag_chunks` guard skips RAG gracefully until then.

# Architecture and scope

This is a new synthetic, dependency-free **mini demonstration** of the evidence-first principles used in the larger private SteedAtlas system. Nothing here is a copy of the private database, old frontend bundles, video assets, or operational credentials.

1. Normalize a question for Chinese name/alias retrieval (without altering the displayed source quote).
2. Rank safe passages with character-bigram BM25; enforce genre, visibility and synthetic-data rights.
3. Check revision, SHA-256, exact text span and source state. Textual occurrence is not historical factual support.
4. Prioritize explicit opposing synthetic labels for the same proposition and same entity within the Top-k budget; disclose truncation.
5. Run a bounded, deterministic read-only research workflow with tool allowlist and trace. It is not an LLM autonomous agent.

Run `python demo.py --agent --query "赤云"` followed by `python -m unittest discover -s tests -v`.

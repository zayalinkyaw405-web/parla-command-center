# Rule: Windows Python Development & Metric Learning Resilience

## 1. CLI Output Invariant (CP1252 Safety)
- On Windows systems, default console streams may use `cp1252` encoding.
- Never use non-ASCII glyphs (e.g., `✓`, `✗`, `•`, special unicode emoticons) in console `print()` calls in test suites and CLI tools.
- Always use standard ASCII tokens: `[PASS]`, `[FAIL]`, `[INFO]`, `[WARN]`, or simple hyphens `-`.

## 2. Metric Embedding Manifold Hygiene
- When extracting feature vectors for metric similarity search (cosine distance / dot product):
  - Always zero-center the feature array ($x - \bar{x}$) before $L_2$ normalization.
  - Raw non-negative features cause artificial high baseline similarity across unrelated classes.

## 3. SQLite Test Database Teardown on Windows
- Windows strictly locks open SQLite files. Before calling `os.remove()` on a test database:
  - Explicitly delete database wrapper references.
  - Call `import gc; gc.collect()`.
  - Wrap file removal in `try...except OSError:` blocks.

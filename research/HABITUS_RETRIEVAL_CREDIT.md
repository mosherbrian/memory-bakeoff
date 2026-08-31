# Habitus retrieval-credit patch needed for the Quality Loop experiment

Stock Habitus exposes retrieval traces in `RecallResult`/`RetrievalPacket`, but its
`record_outcome()` method credits the path attached to an **output decision**. That is
not the same as crediting the memory paths whose retrieved evidence helped solve a task.

For the verified-experience experiment, add an explicit API resembling:

```python
record_retrieval_outcome(
    packet: RetrievalPacket,
    *,
    useful_record_ids: Sequence[str] | None = None,
    verified: bool,
    reward: float,
    receipt_id: str,
)
```

Desired semantics:

1. Do nothing unless the receipt is externally verified.
2. Identify Y-path edges that contributed the credited retrieved records.
3. Reinforce only those paths (or proportionally assign credit when contribution is
   ambiguous).
4. Permit negative credit for paths that repeatedly surface verified-harmful memories.
5. Persist the receipt ID and make updates idempotent.
6. Keep the canonical SQLite evidence immutable; only routing policy should learn.

The benchmark deliberately reports stock Habitus as `supports_feedback=False` until
such an API exists. This prevents accidentally treating SPEAK/LOOK/DO reinforcement as
proof that retrieval itself learns from successful coding trajectories.

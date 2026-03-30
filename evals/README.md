# Evals Directory

This directory contains evaluation datasets and scripts for the Agentic RAG system.

## Structure

```
evals/
├── cases/          # JSON eval case files (question + reference answer + expected chunks)
├── scripts/        # Eval runner scripts (Step 5)
└── README.md
```

## Eval Case Format

```json
{
  "name": "factual_retrieval_basic",
  "question": "What is the capital of France?",
  "reference_answer": "Paris",
  "expected_chunk_ids": [],
  "tags": ["factual", "basic"],
  "meta": {}
}
```

## Running Evals

> Not yet implemented — available in Step 5.

```bash
# Step 5: trigger via API
make eval-run

# Or directly
python -m evals.scripts.run_eval --cases evals/cases/basic.json
```

## Metrics

| Metric | Description |
|--------|-------------|
| `faithfulness` | Answer only uses information in retrieved chunks |
| `answer_relevance` | Answer addresses the question |
| `retrieval_precision` | Fraction of retrieved chunks in expected_chunk_ids |
| `retrieval_recall` | Fraction of expected_chunk_ids in retrieved chunks |
| `abstain_rate` | Fraction of cases where agent abstained |
| `pass_rate` | Fraction of cases that passed all thresholds |

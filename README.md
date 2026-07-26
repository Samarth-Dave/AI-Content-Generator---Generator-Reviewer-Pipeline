# Eklavya AI Content Pipeline

This repository contains the original Part 1 pipeline and the governed Part 2 upgrade. Part 2 is the primary backend path: a FastAPI service and synchronous orchestration flow that produces one auditable RunArtifact per run.

## Part 2 Overview

Part 2 extends the generator/reviewer workflow into a bounded, schema-validated, auditable pipeline. Every run records the draft content, each review, each refinement, the final decision, and timestamps in one stored artifact.

## Agent Roles

Generator: drafts grade-appropriate educational content as a strict GeneratorOutputV2 with an explanation, MCQs, and teacher notes. It uses structured Groq output and retries once if the response fails schema validation.

Reviewer: evaluates the draft quantitatively with 1-5 scores for age appropriateness, correctness, clarity, and coverage. The Python code computes the final pass value deterministically from those scores and rejects invalid feedback paths before continuing.

Refiner: rewrites a failing draft using reviewer feedback. It is bounded to at most two refinements per run, and every refinement attempt is recorded in the run artifact.

Tagger: classifies approved content only. It runs only when the final status is approved and produces indexing metadata for the stored artifact.

## Pass / Fail Criteria

The reviewer uses these thresholds:

- all four scores must be at least 3
- correctness must be at least 4

That means a run only passes when the content is broadly adequate across the board and the factual quality is held to a stricter bar than the other dimensions.

## Orchestration Decisions

The Part 2 orchestrator uses a bounded loop, not an open-ended retry cycle. It performs the initial review plus up to two refinements, which yields at most three review cycles total. The control flow stops explicitly when content passes, when the refinement cap is reached, or when generation or refinement fails schema validation.

GET /history accepts an optional user_id tag. If omitted, the API returns every stored artifact; if present, it returns only that user's runs, most recent first. This is intentionally a filtering tag rather than a full auth system.

## Trade-offs

Persistence stores the full RunArtifact as JSON in SQLite with a small set of indexed columns for lookup. That keeps the implementation simple while preserving the complete audit trail and leaving a clean path to Postgres later.

user_id is treated as a lightweight history tag rather than a login system. That matches the scope of the assessment and avoids adding auth infrastructure that the spec did not ask for.

The repository keeps the Part 1 code alongside Part 2 instead of deleting it. That preserves the original implementation for reference while making the governed Part 2 path the primary backend flow.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Add your Groq API key and optional database URL to .env.

## Running the API

```bash
uvicorn api.server:app --reload
```

## Live Output

The JSON below is the exact output captured from `output.json` for a real end-to-end run on Grade 5, "Fractions as parts of a whole". It ended with `rejected`, so the Tagger did not run and `final.tags` stayed `null`.

See the full JSON response here: **[`output.json`](./output.json)
```json
{
	"run_id": "2b7eaada-06aa-4e5e-90fb-87f8645eb26d",
	"input": {
		"grade": 5,
		"topic": "Fractions as parts of a whole",
		"user_id": "default_user"
	},
	"final": {
		"status": "rejected",
		"content": {
			"explanation": {
				"text": "Fractions are a way to show part of a whole. Imagine you have a pizza that is cut into 8 slices, and you eat 2 of them. You can write this as 2/8, which means you ate 2 slices out of the total 8 slices. The top number, 2, tells us how many slices you ate, and the bottom number, 8, tells us how many slices there were in total. We can also simplify fractions to make them easier to understand. For example, 2/8 can be simplified to 1/4 by dividing both numbers by 2.",
				"grade": 5
			},
			"mcqs": [
				{
					"question": "If you have a cake that is cut into 12 pieces and you eat 3 of them, what fraction of the cake have you eaten?",
					"options": ["1/4", "1/3", "1/6", "2/3"],
					"correct_index": 1
				}
			],
			"teacher_notes": {
				"learning_objective": "To understand that fractions represent parts of a whole and to be able to write and simplify fractions",
				"common_misconceptions": [
					"Thinking that the top number of a fraction always has to be smaller than the bottom number"
				]
			}
		},
		"tags": null
	}
}
```

## Running the CLI

```bash
python main.py --grade 5 --topic "Fractions as parts of a whole"
```

## Testing

```bash
.venv\Scripts\python -m pytest
```

The mandatory Part 2 tests cover:

- schema validation failure handling
- fail -> refine -> pass orchestration
- fail -> refine -> fail -> reject orchestration

## Environment Variables

```bash
GROQ_API_KEY=your-groq-api-key-here
GROQ_MODEL=llama-3.3-70b-versatile
DATABASE_URL=sqlite:///./part2_runs.db
GROQ_TEMPERATURE_GENERATOR=0.2
GROQ_TEMPERATURE_REVIEWER=0.0
DEMO_MODE=0
```
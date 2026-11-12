# <step ID>: <question or attempted change>

## Minimum entry (for a small step)

- **Before:** question, hypothesis, planned check, and the data it uses (with its split status).
- **Runs:** run IDs from `experiments/runlog.py`, or the command and the revision.
- **Outcome:** what happened, including failures, and what changed in the status of the data.
- **Decision and next step:** adopted, rejected or left open, and why.

Use the full record below when a step has several runs, a held-out set, or a change to `pts/`, the table or the Collider.

- Started: <date, time and timezone>
- Owner: <researcher>; issue: <if applicable>
- Previous step: <link, or first step>
- State: <planned / running / completed / interrupted / set aside>

## Before the attempt

- Question and motivation:
- Hypothesis and expected outcome:
- Evidence that would support or contradict it:
- Planned method, baseline and metrics:
- Known limitations and ambiguous labels:
- Input sources and split status before this attempt:

## Run ledger

Preserve one row per run or link a complete machine-readable sweep ledger. Include failed and interrupted runs. Use a new ID and output location for every rerun.

| Run ID | Code / generator revision or patch | Command and configuration / seeds | Inputs / split / hashes | Output or archive location | Outcome |
|---|---|---|---|---|---|
| <unique ID> | <recoverable version> | <exact command and config link> | <manifest link> | <fresh persistent location> | <success, failure, null, regression, crash or interruption> |

## What happened

- Observations and complete per-case evidence:
- Aggregate results and comparison with the baseline:
- Failures, regressions, exclusions, expected failures and missing cases:
- Unexpected findings or implementation errors:
- Changes to dataset status caused by inspecting these results:

## Interpretation and decision

- What the evidence supports:
- What it does not establish:
- Approach adopted, rejected or left open, and why:
- Preserved prototype / configuration for future reuse:
- Next step and reason: <link when created>

## Corrections and follow-ups

Append dated corrections; retain the original observations. Identify invalidated claims and superseding runs explicitly.

## Use in the project

- Collider / table / measuring code change: <link, or not adopted>
- Supporting validation runs:
- Implementation revision / PR:
- Remaining limitations:
- Possible use elsewhere (PHARMAKON): <only in the internal journal>

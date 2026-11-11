# Retail Property Data Reliability Lab

> **Independent project. Synthetic data. No employer data or internal logic.**

This repository is a small, practical example of how I approach reliable operational data.

```text
Input:   lease + finance + location records
Check:   do the records agree?
Output:  a structured exception report and clear triage questions
```

## In one minute

```text
Problem     Reporting is only useful when source records reconcile.
Approach    Validate keys, relationships, amounts, and currencies.
Result      Give an analyst an actionable list of exceptions to investigate.
```

## What it checks

```text
✓ Duplicate business keys
✓ Active leases without a finance record
✓ Leases without a location record
✓ Finance records without a lease
✓ Currency mismatches
✓ Reported-rent variances
```

## Data used

The pipeline reads three intentionally small CSV files. Every record is fictional.

| Dataset | Purpose |
| --- | --- |
| `leases.csv` | Fictional property lease terms and monthly rent |
| `finance.csv` | Fictional monthly finance records |
| `locations.csv` | Fictional location attributes across U.S., Mexico, and Puerto Rico |

## How it works

```python
leases = read_csv("leases.csv")
finance = read_csv("finance.csv")
locations = read_csv("locations.csv")
```

```python
if lease["lease_status"] == "ACTIVE" and lease["lease_id"] not in finance_lease_ids:
    issues.append("MISSING_FINANCE_RECORD")
```

```python
variance = float(record["reported_rent"]) - float(lease["monthly_rent"])
if variance != 0:
    issues.append("RENT_VARIANCE")
```

The pipeline creates two review-ready files:

```text
output/quality_report.json     Structured findings for a dashboard or workflow
output/triage_questions.md     Plain-language questions for a data owner
```

Example finding:

```json
{
  "code": "MISSING_FINANCE_RECORD",
  "severity": "high",
  "record": "...",
  "detail": "Active lease has no finance record for the reporting period."
}
```

## Run it

```bash
python3 src/run_pipeline.py
```

Run the test:

```bash
python3 tests/test_pipeline.py
```

```text
No third-party packages
No credentials
No cloud account
No external services
```

## Engineering choices

```text
Small inputs       Easy to inspect and explain
Deterministic rules Repeatable results for the same data
Structured output  Ready for a review queue or dashboard
Plain language     Supports technical and business reviewers
Tests included     Confirms key exception types are detected
```

## Portfolio wording

```text
Independent Project — Retail Property Data Reliability Lab

Built a Python data-quality and reconciliation workflow for fictional lease,
finance, and location records. Added duplicate checks, cross-source matching,
rent-variance detection, structured exception reporting, and clear triage
questions for data owners.
```

## Important boundary

```text
This is personal learning work.
It is not an employer project.
It contains no production data, internal documents, screenshots, metrics,
credentials, or proprietary logic.
```

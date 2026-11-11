"""Synthetic retail-property data-quality and reconciliation demonstration."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def duplicate_values(rows: list[dict[str, str]], key: str) -> list[str]:
    counts = Counter(row[key] for row in rows)
    return sorted(value for value, count in counts.items() if count > 1)


def issue(code: str, severity: str, record: str, detail: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "record": record, "detail": detail}


def build_report() -> dict[str, object]:
    leases = read_csv("leases.csv")
    finance = read_csv("finance.csv")
    locations = read_csv("locations.csv")
    issues: list[dict[str, str]] = []

    for name, rows, key in [
        ("lease", leases, "lease_id"),
        ("finance", finance, "finance_id"),
        ("location", locations, "property_id"),
    ]:
        for duplicate in duplicate_values(rows, key):
            issues.append(issue("DUPLICATE_KEY", "high", duplicate, f"Duplicate {name} key."))

    lease_by_id = {row["lease_id"]: row for row in leases}
    location_by_property = {row["property_id"]: row for row in locations}
    finance_lease_ids = {row["lease_id"] for row in finance}

    for lease in leases:
        if lease["lease_status"] == "ACTIVE" and lease["lease_id"] not in finance_lease_ids:
            issues.append(issue(
                "MISSING_FINANCE_RECORD", "high", lease["lease_id"],
                "Active lease has no finance record for the reporting period.",
            ))
        if lease["property_id"] not in location_by_property:
            issues.append(issue(
                "MISSING_LOCATION_RECORD", "high", lease["lease_id"],
                "Lease property is missing a location record.",
            ))

    for record in finance:
        lease = lease_by_id.get(record["lease_id"])
        if lease is None:
            issues.append(issue(
                "ORPHAN_FINANCE_RECORD", "high", record["finance_id"],
                "Finance record references a lease that is not in the lease dataset.",
            ))
            continue
        if record["currency"] != lease["currency"]:
            issues.append(issue(
                "CURRENCY_MISMATCH", "high", record["finance_id"],
                "Finance currency does not match lease currency.",
            ))
        variance = float(record["reported_rent"]) - float(lease["monthly_rent"])
        if variance != 0:
            issues.append(issue(
                "RENT_VARIANCE", "medium", record["finance_id"],
                f"Reported rent differs from lease rent by {variance:.2f} {record['currency']}.",
            ))

    counts = Counter(item["severity"] for item in issues)
    return {
        "project": "Independent Synthetic Retail Property Data Reliability Lab",
        "records_checked": {
            "leases": len(leases), "finance": len(finance), "locations": len(locations)
        },
        "issue_count": len(issues),
        "issues_by_severity": dict(sorted(counts.items())),
        "issues": issues,
    }


def write_outputs(report: dict[str, object]) -> None:
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "quality_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Data Triage Questions", "", "Generated from synthetic records only.", ""]
    for item in report["issues"]:  # type: ignore[index]
        lines.append(f"- **{item['severity'].upper()} — {item['code']} ({item['record']})**: Who owns the source record, and what evidence confirms the correct value? {item['detail']}")
    (OUTPUT / "triage_questions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    report = build_report()
    write_outputs(report)
    print(f"Validated {sum(report['records_checked'].values())} synthetic records.")
    print(f"Found {report['issue_count']} data-quality exceptions.")

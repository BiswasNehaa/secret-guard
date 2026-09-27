"""Console, JSON, CSV, XML, HTML, and SARIF reporting for findings."""

import csv
import hashlib
import html
import io
import json
import os
import sys
import xml.etree.ElementTree as ET

from . import __version__
from .rules import RULES, SPECIAL_RULES

SEVERITY_COLORS = {
    "critical": "\033[31;1m",  # bright red
    "high": "\033[31m",        # red
    "medium": "\033[33m",      # yellow
    "low": "\033[36m",         # cyan
}
RESET = "\033[0m"


SCHEMA_VERSION = 1


def should_color(force=None):
    """force=True/False overrides auto-detection; None means auto (TTY + NO_COLOR)."""
    if force is not None:
        return force
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def mask(value, reveal_prefix=None, reveal_suffix=None):
    if reveal_prefix is None and reveal_suffix is None:
        visible = 6
        if len(value) <= visible + 4:
            return "*" * len(value)
        return value[:visible] + "*" * max(0, len(value) - visible)

    pref_len = max(0, reveal_prefix) if reveal_prefix is not None else 0
    suff_len = max(0, reveal_suffix) if reveal_suffix is not None else 0
    val_len = len(value)

    if pref_len + suff_len >= val_len:
        return "*" * val_len

    middle_stars = val_len - pref_len - suff_len
    suffix_part = value[val_len - suff_len:] if suff_len > 0 else ""
    return value[:pref_len] + "*" * middle_stars + suffix_part


def format_console(
    findings,
    root,
    show_value=True,
    color=None,
    truncated=False,
    total_findings=None,
    reveal_prefix=None,
    reveal_suffix=None,
):
    color = should_color(force=color)
    lines = []
    for finding in sorted(findings, key=lambda f: (f["path"], f["line"])):
        severity = finding["severity"]
        tag = severity.upper().ljust(8)
        if color:
            tag = SEVERITY_COLORS[severity] + tag + RESET
        value = finding["value"][:]
        if not show_value and not finding.get("reveal"):
            value = mask(
                value,
                reveal_prefix=reveal_prefix,
                reveal_suffix=reveal_suffix,
            )
        lines.append(
            "{path}:{line} [{tag}] {rule}: {value}".format(
                path=finding["path"],
                line=finding["line"],
                tag=tag,
                rule=finding["rule"],
                value=value,
            )
        )
    lines.append("")
    summary = summarize(findings)
    if truncated:
        summary["truncated"] = total_findings - len(findings)
        summary_line = (
            "{critical} critical, {high} high, {medium} medium, {low} low — "
            "{total} total (showing {shown} of {total_findings}; "
            "{truncated} truncated)"
        ).format(
            critical=summary["critical"],
            high=summary["high"],
            medium=summary["medium"],
            low=summary["low"],
            total=summary["total"],
            shown=len(findings),
            total_findings=total_findings,
            truncated=summary["truncated"],
        )
    else:
        summary_line = (
            "{critical} critical, {high} high, {medium} medium, {low} low — "
            "{total} total"
        ).format(
            critical=summary["critical"],
            high=summary["high"],
            medium=summary["medium"],
            low=summary["low"],
            total=summary["total"],
        )
    if color:
        summary_line = (
            "\033[31m{critical}\033[0m critical, "
            "\033[31m{high}\033[0m high, "
            "\033[33m{medium}\033[0m medium, "
            "\033[36m{low}\033[0m low — {total} total"
        ).format(**summary)
    lines.append(summary_line)
    return "\n".join(lines)


def format_summary(
    findings,
    root,
    show_value=True,
    color=None,
    truncated=False,
    total_findings=None,
    reveal_prefix=None,
    reveal_suffix=None,
):
    """Render only the concise severity summary, omitting per-finding lines.

    Useful for CI logs where the full report is noise but an aggregate count
    is still wanted. Mirrors the trailing summary line of format_console.
    """

    color = should_color(force=color)
    summary = summarize(findings)
    if truncated:
        summary["truncated"] = total_findings - len(findings)
        summary_line = (
            "{critical} critical, {high} high, {medium} medium, {low} low — "
            "{total} total (showing {shown} of {total_findings}; "
            "{truncated} truncated)"
        ).format(
            critical=summary["critical"],
            high=summary["high"],
            medium=summary["medium"],
            low=summary["low"],
            total=summary["total"],
            shown=len(findings),
            total_findings=total_findings,
            truncated=summary["truncated"],
        )
    else:
        summary_line = (
            "{critical} critical, {high} high, {medium} medium, {low} low — "
            "{total} total"
        ).format(
            critical=summary["critical"],
            high=summary["high"],
            medium=summary["medium"],
            low=summary["low"],
            total=summary["total"],
        )
    if color:
        summary_line = (
            "\033[31m{critical}\033[0m critical, "
            "\033[31m{high}\033[0m high, "
            "\033[33m{medium}\033[0m medium, "
            "\033[36m{low}\033[0m low — {total} total"
        ).format(**summary)
    return summary_line


def summarize(findings):
    total = len(findings)
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for finding in findings:
        level = counts.get(finding["severity"])
        if level is None:
            continue
        counts[finding["severity"]] = level + 1
    counts["total"] = total
    return counts


def format_json(
    findings,
    root,
    show_value=False,
    truncated=False,
    total_findings=None,
    reveal_prefix=None,
    reveal_suffix=None,
):
    ordered = sorted(findings, key=lambda f: (f["path"], f["line"], f["rule"]))
    sanitized = []
    for finding in ordered:
        item = dict(finding)
        if not show_value and not finding.get("reveal"):
            item["value"] = mask(
                item["value"],
                reveal_prefix=reveal_prefix,
                reveal_suffix=reveal_suffix,
            )
        sanitized.append(item)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "root": root,
        "findings": sanitized,
    }
    if truncated:
        payload["truncated"] = True
        payload["total_findings"] = total_findings
    return json.dumps(payload, indent=2)


CSV_COLUMNS = ("path", "line", "severity", "rule", "rule_id", "value", "description")


def format_csv(
    findings,
    root,
    show_value=False,
    truncated=False,
    total_findings=None,
    reveal_prefix=None,
    reveal_suffix=None,
):
    """Render findings as a CSV table with a header row and one row per finding.

    Values are masked unless show_value is set or the finding opts in to
    reveal, matching format_json. Any tricky characters (commas, quotes,
    newlines) in secret values are quoted/escaped by the csv module.
    """

    ordered = sorted(findings, key=lambda f: (f["path"], f["line"], f["rule"]))
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(CSV_COLUMNS)
    for finding in ordered:
        value = finding["value"][:]
        if not show_value and not finding.get("reveal"):
            value = mask(
                value,
                reveal_prefix=reveal_prefix,
                reveal_suffix=reveal_suffix,
            )
        writer.writerow(
            [
                finding["path"],
                finding["line"],
                finding["severity"],
                finding["rule"],
                finding["rule_id"],
                value,
                finding["description"],
            ]
        )
    return buf.getvalue()


def _masked_value(finding, show_value, reveal_prefix, reveal_suffix):
    """The value to emit for a finding, masked unless revealed."""
    value = finding["value"][:]
    if not show_value and not finding.get("reveal"):
        value = mask(
            value, reveal_prefix=reveal_prefix, reveal_suffix=reveal_suffix
        )
    return value


def format_xml(
    findings,
    root,
    show_value=False,
    truncated=False,
    total_findings=None,
    reveal_prefix=None,
    reveal_suffix=None,
):
    """Render findings as a JUnit-style XML report.

    Each finding becomes a failing ``testcase`` whose attributes carry every
    finding field (path, line, severity, rule, rule_id, and the masked value)
    plus a ``failure`` node with the description. Values are masked unless
    show_value is set, matching format_json / format_csv.
    """

    ordered = sorted(findings, key=lambda f: (f["path"], f["line"], f["rule"]))
    count = len(ordered)
    suites = ET.Element(
        "testsuites",
        {
            "name": "secret-guard",
            "tests": str(count),
            "failures": str(count),
            "errors": "0",
            "time": "0",
        },
    )
    suite = ET.SubElement(
        suites,
        "testsuite",
        {
            "name": "secret-guard scan",
            "tests": str(count),
            "failures": str(count),
            "errors": "0",
            "skipped": "0",
            "time": "0",
        },
    )
    if truncated:
        suite.set("truncated", "true")
        suite.set("total_findings", str(total_findings))
    for finding in ordered:
        value = _masked_value(finding, show_value, reveal_prefix, reveal_suffix)
        testcase = ET.SubElement(
            suite,
            "testcase",
            {
                "name": value,
                "classname": "{}:{}".format(finding["path"], finding["line"]),
                "time": "0",
                "path": finding["path"],
                "line": str(finding["line"]),
                "severity": finding["severity"],
                "rule": finding["rule"],
                "rule_id": finding["rule_id"],
            },
        )
        failure = ET.SubElement(
            testcase,
            "failure",
            {"type": finding["severity"], "message": finding["description"]},
        )
        failure.text = value
    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    return header + ET.tostring(suites, encoding="unicode")


def format_html(
    findings,
    root,
    show_value=False,
    truncated=False,
    total_findings=None,
    reveal_prefix=None,
    reveal_suffix=None,
):
    """Render findings as a self-contained HTML report.

    The output inlines every style so the report can be saved or emailed and
    rendered anywhere. All finding fields are shown and values are masked
    unless show_value is set.
    """

    ordered = sorted(findings, key=lambda f: (f["path"], f["line"], f["rule"]))
    summary = summarize(findings)
    count = len(ordered)

    def esc(text):
        return html.escape(str(text))

    rows = []
    for finding in ordered:
        severity = finding["severity"]
        rows.append(
            "<tr>"
            "<td>{path}</td>"
            "<td>{line}</td>"
            "<td class=\"sev-{sev}\">{sev}</td>"
            "<td>{rule}</td>"
            "<td>{rule_id}</td>"
            "<td><code>{value}</code></td>"
            "<td>{desc}</td>"
            "</tr>".format(
                path=esc(finding["path"]),
                line=esc(finding["line"]),
                sev=esc(severity),
                rule=esc(finding["rule"]),
                rule_id=esc(finding["rule_id"]),
                value=esc(
                    _masked_value(finding, show_value, reveal_prefix, reveal_suffix)
                ),
                desc=esc(finding["description"]),
            )
        )
    truncation_note = ""
    if truncated:
        truncation_note = (
            f"<p><strong>Note:</strong> showing {count} of "
            f"{esc(total_findings)} findings "
            f"({esc(total_findings - count)} truncated).</p>"
        )
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<title>secret-guard scan report</title>\n"
        "<style>\n"
        "body {{ font-family: -apple-system, Segoe UI, Roboto, "
        "Helvetica, Arial, sans-serif; }}\n"
        "table {{ border-collapse: collapse; width: 100%; }}\n"
        "th, td {{ border: 1px solid #ddd; padding: 6px 10px; "
        "text-align: left; }}\n"
        "th {{ background: #f5f5f5; }}\n"
        "code {{ background: #f5f5f5; padding: 1px 4px; border-radius: 3px; }}\n"
        ".sev-critical {{ color: #b60205; font-weight: bold; }}\n"
        ".sev-high {{ color: #d93f0b; }}\n"
        ".sev-medium {{ color: #b08800; }}\n"
        ".sev-low {{ color: #0969da; }}\n"
        "</style>\n"
        "</head>\n<body>\n"
        "<h1>secret-guard scan report</h1>\n"
        "<p>Scanned path: <code>{root}</code></p>\n"
        "<p><strong>{total} finding(s):</strong> "
        "{critical} critical, {high} high, {medium} medium, {low} low.</p>\n"
        "{truncation_note}"
        "<h2>Findings</h2>\n"
        "<table>\n"
        "<thead><tr><th>Path</th><th>Line</th><th>Severity</th><th>Rule</th>"
        "<th>Rule ID</th><th>Value</th><th>Description</th></tr></thead>\n"
        "<tbody>\n{rows}\n</tbody>\n</table>\n"
        "</body>\n</html>\n"
    ).format(
        root=esc(root),
        total=esc(summary["total"]),
        critical=esc(summary["critical"]),
        high=esc(summary["high"]),
        medium=esc(summary["medium"]),
        low=esc(summary["low"]),
        truncation_note=truncation_note,
        rows="\n".join(rows),
    )


SARIF_SCHEMA_URI = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/"
    "sarif-schema-2.1.0.json"
)
SARIF_VERSION = "2.1.0"
SARIF_SEVERITY = {
    "critical": {"level": "error", "security-severity": "9.5"},
    "high": {"level": "error", "security-severity": "7.5"},
    "medium": {"level": "warning", "security-severity": "5.0"},
    "low": {"level": "note", "security-severity": "2.0"},
}


def _rule_catalog():
    """Map every known rule id to its generic {name, severity, description}.

    Built-ins come from RULES/SPECIAL_RULES; a rule id outside that (a
    custom rule) falls back to the reporting finding's own fields.
    """

    catalog = {rule["id"]: rule for rule in RULES}
    catalog.update(SPECIAL_RULES)
    return catalog


def format_sarif(
    findings,
    root,
    show_value=False,
    truncated=False,
    total_findings=None,
    reveal_prefix=None,
    reveal_suffix=None,
):
    """Render findings as a SARIF 2.1.0 log for GitHub Code Scanning.

    Secret values are always masked here, regardless of show_value —
    SARIF logs are meant to be uploaded and retained by Code Scanning, so
    raw secret material must never end up in one. A finding that opts in to
    ``reveal`` (a dotenv variable name, never the secret's actual value) is
    shown as-is, matching the other reporters. A one-way hash of the raw
    value is included as a fingerprint so the same secret can be tracked
    across scans without exposing it.
    """

    ordered = sorted(findings, key=lambda f: (f["path"], f["line"], f["rule"]))
    catalog = _rule_catalog()

    rule_order = []
    rule_defs = {}
    for finding in ordered:
        rule_id = finding["rule_id"]
        if rule_id in rule_defs:
            continue
        meta = catalog.get(
            rule_id,
            {
                "name": finding["rule"],
                "severity": finding["severity"],
                "description": finding["description"],
            },
        )
        sev = SARIF_SEVERITY.get(meta["severity"], SARIF_SEVERITY["medium"])
        rule_order.append(rule_id)
        rule_defs[rule_id] = {
            "id": rule_id,
            "name": meta["name"],
            "shortDescription": {"text": meta["name"]},
            "fullDescription": {"text": meta["description"]},
            "defaultConfiguration": {"level": sev["level"]},
            "properties": {
                "security-severity": sev["security-severity"],
                "tags": ["security", "secrets"],
            },
        }
    rule_index = {rule_id: i for i, rule_id in enumerate(rule_order)}

    results = []
    for finding in ordered:
        rule_id = finding["rule_id"]
        sev = SARIF_SEVERITY.get(finding["severity"], SARIF_SEVERITY["medium"])
        value = _masked_value(finding, False, reveal_prefix, reveal_suffix)
        results.append(
            {
                "ruleId": rule_id,
                "ruleIndex": rule_index[rule_id],
                "level": sev["level"],
                "message": {
                    "text": "{}: {}".format(finding["rule"], value),
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": finding["path"].replace(os.sep, "/"),
                            },
                            "region": {"startLine": finding["line"]},
                        }
                    }
                ],
                "partialFingerprints": {
                    "secretGuardValueHash/v1": hashlib.sha256(
                        finding["value"].encode("utf-8")
                    ).hexdigest(),
                },
            }
        )

    run = {
        "tool": {
            "driver": {
                "name": "secret-guard",
                "informationUri": "https://github.com/taksh1507/secret-guard",
                "version": __version__,
                "rules": [rule_defs[rule_id] for rule_id in rule_order],
            }
        },
        "results": results,
    }
    if truncated:
        run["properties"] = {
            "truncated": True,
            "total_findings": total_findings,
        }

    sarif = {
        "$schema": SARIF_SCHEMA_URI,
        "version": SARIF_VERSION,
        "runs": [run],
    }
    return json.dumps(sarif, indent=2)
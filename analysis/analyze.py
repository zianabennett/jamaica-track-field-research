#!/usr/bin/env python3
"""Validate the local evidence corpus and reproduce its descriptive outputs.

Uses only the Python standard library. Does not access the network, install
packages, or measure athletes. Run from any working directory.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import html
import json
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_HOSTS = {
    "issasports.com", "athleticsja.org", "www.utech.edu.jm",
    "www.mona.uwi.edu", "gcfc.edu.jm", "jadco.gov.jm",
    "sdf.org.jm", "joa.org.jm",
}


def read_json(relative_path):
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(codebook, entities, sources):
    snapshot = date.fromisoformat(codebook["snapshot_date"])
    role_ids = [r["id"] for r in codebook["roles"]]
    source_ids = [s["id"] for s in sources]
    entity_ids = [e["id"] for e in entities]
    require(len(role_ids) == len(set(role_ids)), "Duplicate role IDs")
    require(len(source_ids) == len(set(source_ids)), "Duplicate source IDs")
    require(len(entity_ids) == len(set(entity_ids)), "Duplicate institution IDs")
    require(bool(entities) and bool(sources), "Empty corpus")
    for source in sources:
        url = urlparse(source["url"])
        require(url.scheme == "https", f"Non-HTTPS source: {source['id']}")
        require(url.netloc in ALLOWED_HOSTS, f"Unexpected publisher host: {url.netloc}")
        require(date.fromisoformat(source["accessed"]) <= snapshot, "Access after snapshot")
        if source["publication_date"]:
            require(date.fromisoformat(source["publication_date"]) <= snapshot,
                    "Publication after snapshot")
    for entity in entities:
        require(entity["entity_type"] in codebook["entity_types"], "Unknown entity type")
        assigned = [r["role_id"] for r in entity["roles"]]
        require(assigned and len(assigned) == len(set(assigned)),
                f"Empty or duplicate roles: {entity['id']}")
        for role in entity["roles"]:
            require(role["role_id"] in role_ids, "Unknown role")
            require(bool(role["source_ids"]), "Unsupported role")
            require(set(role["source_ids"]) <= set(source_ids), "Unknown source reference")
            require(bool(role["observation"].strip()), "Empty evidence observation")


def source_links(source_ids, prefix="../sources/source-register.md"):
    return ", ".join(f"[{sid}]({prefix}#{sid.lower()})" for sid in source_ids)


def render_sources(sources):
    access_dates = sorted({source["accessed"] for source in sources})
    date_note = (f"Pages were retrieved between {access_dates[0]} and {access_dates[-1]}. "
                 if len(access_dates) > 1 else f"All pages were retrieved on {access_dates[0]}. ")
    lines = ["# Source register", "", date_note +
             "These entries contain original research notes and links, not copied page archives.", ""]
    for source in sources:
        lines.extend([
            f"## {source['id']}", "",
            f"**[{source['title']}]({source['url']})**", "",
            f"Publisher: {source['publisher']}. Accessed: {source['accessed']}. "
            f"Publication date: {source['publication_date'] or 'not established from the page'}.", "",
            f"Primary-source basis: {source['primary_source_basis']}", "",
            f"Evidence location: {source['relevant_section']}.", "",
            f"Limit: {source['limitation']}", "",
        ])
    return "\n".join(lines)


def render_evidence(entities, codebook):
    role_labels = {r["id"]: r["label"] for r in codebook["roles"]}
    lines = ["# Evidence matrix", "", "One row is one institution-function assignment. "
             "Functions can overlap. Unlisted functions are not established by this corpus; "
             "they are not proven absent.", "",
             "| Institution | Coded function | Evidence observation | Sources |",
             "| --- | --- | --- | --- |"]
    for entity in entities:
        for role in entity["roles"]:
            lines.append(f"| {entity['id']} | {role_labels[role['role_id']]} | "
                         f"{role['observation']} | {source_links(role['source_ids'])} |")
    lines.extend(["", "Institution names and type classifications are in "
                  "[the input dataset](../data/institutions.json). Coding definitions are in "
                  "[the method](../method.md).", ""])
    return "\n".join(lines)


def compute_counts(entities):
    roles = Counter(r["role_id"] for e in entities for r in e["roles"])
    types = Counter(e["entity_type"] for e in entities)
    return roles, types


def render_summary(entities, sources, codebook, roles, types):
    n = len(entities)
    assignments = sum(roles.values())
    lines = ["# Reproduced descriptive results", "",
             f"Corpus snapshot: {codebook['snapshot_date']}.", "",
             f"The dataset contains **{n} institutions**, **{len(sources)} primary-source pages**, "
             f"and **{assignments} documented institution-function assignments** across "
             f"**{len(codebook['roles'])} coded functions**.", "",
             "These counts describe a purposively selected evidence corpus. They do not estimate "
             "national prevalence, funding, service capacity, athlete access, or sporting success.", "",
             "## Documented functions", "",
             "| Function | Institutions | Share of this sample | Institution IDs |",
             "| --- | ---: | ---: | --- |"]
    for role in codebook["roles"]:
        members = [e["id"] for e in entities if any(r["role_id"] == role["id"] for r in e["roles"])]
        lines.append(f"| {role['label']} | {roles[role['id']]} | "
                     f"{roles[role['id']] / n:.1%} | {', '.join(members) or 'None'} |")
    lines.extend(["", "An institution can appear in several rows. Percentages are not intended to sum to 100%.", "",
                  "## Institution types", "",
                  "| Type | Count |", "| --- | ---: |"])
    for key, label in codebook["entity_types"].items():
        lines.append(f"| {label} | {types[key]} |")
    lines.extend(["", "## Coverage and coding checks", "",
                  f"- Each of the {n} institutions has at least one evidence-backed function.",
                  f"- Every one of the {assignments} assignments resolves to registered source IDs.",
                  "- IDs are unique; duplicate institution-function assignments are rejected.",
                  "- Access and publication dates do not exceed the snapshot date.", "",
                  "These are structural checks of the local dataset. They do not independently verify "
                  "institutional claims or the current operation of services.", "",
                  "[Read the evidence matrix](evidence-matrix.md) · "
                  "[Read the interpretation](../findings.md) · "
                  "[Read the method](../method.md)", ""])
    return "\n".join(lines)


def render_svg(codebook, roles, n):
    width, height = 980, 660
    left, top, row_h, unit = 355, 150, 49, 110
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">Documented institutional support functions</title>',
             '<desc id="desc">Counts of institutions with each documented function in a purposive sample of eight. This is not a national census or a ranking.</desc>',
             '<rect width="980" height="660" fill="#f8fafc"/>',
             '<g font-family="Arial, Helvetica, sans-serif" fill="#172b3a">',
             '<text x="36" y="48" font-size="25" font-weight="700">Documented support functions</text>',
             f'<text x="36" y="79" font-size="16">Eight sampled institutions · Source snapshot {html.escape(codebook["snapshot_date"])}</text>',
             '<text x="36" y="106" font-size="14" fill="#526372">An institution can appear in several categories.</text>']
    for tick in range(5):
        x = left + tick * unit
        parts.append(f'<line x1="{x}" y1="{top - 22}" x2="{x}" y2="{top + 7 * row_h + 30}" stroke="#d5dee5"/>')
        parts.append(f'<text x="{x}" y="{top - 30}" text-anchor="middle" font-size="13">{tick}</text>')
    for i, role in enumerate(codebook["roles"]):
        y = top + i * row_h
        count = roles[role["id"]]
        label = html.escape(role["label"])
        parts.append(f'<text x="36" y="{y + 20}" font-size="15">{label}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{count * unit}" height="30" rx="4" fill="#176b66"/>')
        parts.append(f'<text x="{left + count * unit + 12}" y="{y + 21}" font-size="15" font-weight="700">{count} / {n}</text>')
    parts.extend(['<text x="36" y="594" font-size="14">Counts describe this selected corpus, not national coverage, quality, or impact.</text>',
                  '<text x="36" y="620" font-size="13" fill="#526372">Reproduce from data/institutions.json with analysis/analyze.py</text>', '</g>', '</svg>'])
    svg = "\n".join(parts) + "\n"
    ET.fromstring(svg)
    return svg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate inputs and compare saved outputs without rewriting them")
    args = parser.parse_args()
    codebook = read_json("data/codebook.json")
    entities = read_json("data/institutions.json")
    sources = read_json("sources/source-register.json")
    validate(codebook, entities, sources)
    roles, types = compute_counts(entities)
    outputs = {
        "sources/source-register.md": render_sources(sources),
        "results/evidence-matrix.md": render_evidence(entities, codebook),
        "results/summary.md": render_summary(entities, sources, codebook, roles, types),
        "assets/support-functions.svg": render_svg(codebook, roles, len(entities)),
    }
    for relative, content in outputs.items():
        path = ROOT / relative
        if args.check:
            require(path.exists(), f"Missing output: {relative}")
            require(path.read_text(encoding="utf-8") == content, f"Stale output: {relative}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    mode = "Checked" if args.check else "Generated"
    print(f"{mode} {len(outputs)} outputs from {len(entities)} institutions, "
          f"{len(sources)} sources, and {sum(roles.values())} role assignments.")


if __name__ == "__main__":
    main()

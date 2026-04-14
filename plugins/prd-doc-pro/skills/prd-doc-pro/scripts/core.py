#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD Doc Pro Core — BM25 search engine for PRD knowledge base
"""

import csv
import re
from pathlib import Path
from math import log
from collections import defaultdict
from typing import Optional, List, Dict, Any

DATA_DIR = Path(__file__).parent.parent / "data"
MAX_RESULTS = 3

CSV_CONFIG = {
    "product-type": {
        "file": "product-types.csv",
        "search_cols": ["Product Type", "Keywords", "Key Considerations", "Metric Focus"],
        "output_cols": ["Product Type", "PRD Template", "Recommended Depth", "Sections Order",
                        "Primary Personas", "Metric Focus", "Key Considerations", "Common Out-of-Scope Mistakes"]
    },
    "section": {
        "file": "sections.csv",
        "search_cols": ["Section Name", "Keywords", "Purpose"],
        "output_cols": ["Section Name", "Purpose", "Required For", "Priority",
                        "Template", "Writing Tips", "Common Mistakes", "Word Count Guide"]
    },
    "user-story": {
        "file": "user-stories.csv",
        "search_cols": ["Story Category", "Keywords", "Typical Persona", "SaaS Context Notes"],
        "output_cols": ["Story Category", "Typical Persona", "Good Story Example", "Bad Story Example",
                        "AC Format", "AC Example", "INVEST Issues to Watch", "SaaS Context Notes"]
    },
    "antipattern": {
        "file": "antipatterns.csv",
        "search_cols": ["Antipattern Name", "Keywords", "Symptom", "Affects Section"],
        "output_cols": ["Antipattern Name", "Affects Section", "Symptom", "Root Cause",
                        "Impact", "Bad Example", "Good Example", "Fix"]
    },
    "metric": {
        "file": "metrics.csv",
        "search_cols": ["Metric Name", "Keywords", "Category", "SaaS Type", "Why It Matters"],
        "output_cols": ["Metric Name", "Category", "Product Stage", "SaaS Type", "Definition",
                        "Formula / Measurement", "Target Benchmark", "Why It Matters", "Anti-Metric Warning"]
    },
    "template": {
        "file": "templates.csv",
        "search_cols": ["Template Name", "Keywords", "Use When", "Notes"],
        "output_cols": ["Template Name", "Use When", "Length Guide", "Required Sections",
                        "Optional Sections", "Markdown Template", "Notes"]
    },
    "platform-rules": {
        "file": "platform-rules.csv",
        "search_cols": ["Rule Name", "Platform", "Keywords", "Category", "Requirement"],
        "output_cols": ["Rule Name", "Platform", "Category", "Guideline Reference",
                        "Requirement", "Impact If Violated", "PRD Action Required", "Common Mistakes"]
    },
    "mobile-ux": {
        "file": "mobile-ux.csv",
        "search_cols": ["Pattern Name", "Platform", "Keywords", "Category", "Description"],
        "output_cols": ["Pattern Name", "Platform", "Category", "Description",
                        "When to Use", "PRD Guidance", "Good Example", "Bad Example", "Accessibility Note"]
    },
}

AVAILABLE_DOMAINS = list(CSV_CONFIG.keys())


# ──────────────────────────────────────────────
# BM25 implementation
# ──────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    text = text.lower()
    return re.findall(r"\b[a-z0-9][a-z0-9\-']*\b", text)


def _build_index(docs: List[Dict], search_cols: List[str]):
    """Build inverted index and document lengths for BM25."""
    inv_idx: Dict[str, List] = defaultdict(list)
    doc_lengths: List[int] = []

    for doc_id, doc in enumerate(docs):
        combined = " ".join(str(doc.get(col, "")) for col in search_cols)
        tokens = _tokenize(combined)
        doc_lengths.append(len(tokens))

        term_freq: Dict[str, int] = defaultdict(int)
        for t in tokens:
            term_freq[t] += 1
        for term, freq in term_freq.items():
            inv_idx[term].append((doc_id, freq))

    return inv_idx, doc_lengths


def _bm25_score(query_terms, inv_idx, doc_lengths, n_docs, k1=1.5, b=0.75):
    avg_dl = sum(doc_lengths) / max(n_docs, 1)
    scores: Dict[int, float] = defaultdict(float)

    for term in query_terms:
        if term not in inv_idx:
            continue
        postings = inv_idx[term]
        df = len(postings)
        idf = log((n_docs - df + 0.5) / (df + 0.5) + 1)
        for doc_id, tf in postings:
            dl = doc_lengths[doc_id]
            norm_tf = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg_dl))
            scores[doc_id] += idf * norm_tf

    return scores


def search(query: str, domain: Optional[str] = None, max_results: int = MAX_RESULTS) -> Dict:
    """Search the PRD knowledge base across a domain (or all domains)."""
    if domain and domain not in CSV_CONFIG:
        return {"error": f"Unknown domain '{domain}'. Available: {', '.join(AVAILABLE_DOMAINS)}"}

    domains_to_search = [domain] if domain else AVAILABLE_DOMAINS
    all_results = []

    for d in domains_to_search:
        cfg = CSV_CONFIG[d]
        file_path = DATA_DIR / cfg["file"]
        if not file_path.exists():
            continue

        with open(file_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            docs = list(reader)

        if not docs:
            continue

        inv_idx, doc_lengths = _build_index(docs, cfg["search_cols"])
        query_terms = _tokenize(query)
        scores = _bm25_score(query_terms, inv_idx, doc_lengths, len(docs))

        for doc_id, score in sorted(scores.items(), key=lambda x: -x[1])[:max_results]:
            if score > 0:
                row = {k: docs[doc_id].get(k, "") for k in cfg["output_cols"] if k in docs[doc_id]}
                all_results.append({"domain": d, "score": round(score, 3), "data": row})

    all_results.sort(key=lambda x: -x["score"])

    if not all_results:
        return {
            "query": query,
            "domain": domain or "all",
            "count": 0,
            "results": [],
            "message": "No results found. Try broader keywords."
        }

    return {
        "query": query,
        "domain": domain or "all",
        "count": len(all_results[:max_results]),
        "results": [r["data"] for r in all_results[:max_results]],
        "domains_hit": list({r["domain"] for r in all_results[:max_results]})
    }


def search_domain(query: str, domain: str, max_results: int = MAX_RESULTS) -> Dict:
    """Convenience wrapper for single-domain search."""
    return search(query, domain=domain, max_results=max_results)


def load_all_rows(domain: str) -> List[Dict]:
    """Load all rows from a domain CSV (used by the PRD generator)."""
    cfg = CSV_CONFIG.get(domain)
    if not cfg:
        return []
    file_path = DATA_DIR / cfg["file"]
    if not file_path.exists():
        return []
    with open(file_path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

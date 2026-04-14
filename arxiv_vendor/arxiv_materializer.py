#!/usr/bin/env python3
"""
arXiv Metadata Materializer — Lazy materialization of arXiv paper metadata.

Reads arxiv_seed.yaml, fetches metadata via arXiv API, writes JSONL manifests
with per-line SHA-256 hashes. Supports bounded sampling for seed verification
and unbounded full fetch for later materialization waves.

Standard: Yeshua
Version: 1.0.0
"""

import argparse
import hashlib
import json
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


class ArxivMaterializer:
    """Materializes arXiv metadata on demand."""

    NS = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    def __init__(self, seed_path: str, output_dir: str):
        self.seed_path = Path(seed_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with open(self.seed_path, "r") as f:
            self.seed = yaml.safe_load(f)
        self.fetch_cfg = self.seed.get("fetch", {})
        self.delay = self.fetch_cfg.get("delay_seconds", 3)
        self.max_results = self.fetch_cfg.get("max_results_per_request", 1000)
        self.api_base = self.seed["root"]["api_base"]

    def _fetch_page(self, query: str, start: int, max_results: int) -> ET.Element:
        url = (
            f"{self.api_base}?"
            f"search_query={urllib.parse.quote(query)}"
            f"&start={start}&max_results={max_results}"
            f"&sortBy={self.fetch_cfg.get('sort_by', 'submittedDate')}"
            f"&sortOrder={self.fetch_cfg.get('sort_order', 'descending')}"
        )
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "orthogonal-engineering-arxiv-materializer/1.0"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        return ET.fromstring(data)

    def _parse_entry(self, entry: ET.Element) -> Optional[Dict[str, any]]:
        """Parse an Atom entry into a metadata dict."""
        id_elem = entry.find("atom:id", self.NS)
        if id_elem is None:
            return None
        arxiv_id = id_elem.text.split("/")[-1]
        title = (entry.find("atom:title", self.NS).text or "").strip()
        summary = (entry.find("atom:summary", self.NS).text or "").strip()
        published = (entry.find("atom:published", self.NS).text or "").strip()
        updated = (entry.find("atom:updated", self.NS).text or "").strip()

        authors = []
        for author in entry.findall("atom:author", self.NS):
            name = author.find("atom:name", self.NS)
            if name is not None:
                authors.append(name.text)

        categories = []
        for cat in entry.findall("atom:category", self.NS):
            term = cat.get("term")
            if term:
                categories.append(term)

        primary = entry.find("arxiv:primary_category", self.NS)
        primary_category = primary.get("term") if primary is not None else None

        license_url = ""
        rights = entry.find("atom:rights", self.NS)
        if rights is not None and rights.text:
            license_url = rights.text.strip()

        return {
            "arxiv_id": arxiv_id,
            "title": title,
            "authors": authors,
            "abstract": summary,
            "categories": categories,
            "primary_category": primary_category,
            "published": published,
            "updated": updated,
            "license": license_url,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
        }

    def materialize_category(
        self,
        category: Dict[str, str],
        max_papers: Optional[int] = None,
    ) -> Dict[str, any]:
        """Fetch metadata for a single category."""
        cat_id = category["id"]
        query = category["query"]
        target = max_papers if max_papers is not None else 10_000_000
        print(f"Materializing category {cat_id} (target ~{target} papers)...")

        records: List[Dict[str, any]] = []
        start = 0
        while start < target:
            page_size = min(self.max_results, target - start)
            try:
                root = self._fetch_page(query, start, page_size)
            except Exception as e:
                print(f"  ERROR fetching {cat_id} start={start}: {e}", file=sys.stderr)
                break

            entries = root.findall("atom:entry", self.NS)
            if not entries:
                break

            for entry in entries:
                rec = self._parse_entry(entry)
                if rec:
                    records.append(rec)

            print(f"  Fetched {len(entries)} entries (total {len(records)})")
            start += len(entries)
            if len(entries) < page_size:
                break
            if start < target:
                time.sleep(self.delay)

        # Write JSONL with per-line SHA-256 hashes
        jsonl_path = self.output_dir / f"{cat_id.replace('.', '_')}.jsonl"
        hashes: List[str] = []
        with open(jsonl_path, "w") as f:
            for rec in records:
                line = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
                f.write(line + "\n")
                hashes.append(hashlib.sha256(line.encode("utf-8")).hexdigest())

        # Write hash manifest
        hash_path = self.output_dir / f"{cat_id.replace('.', '_')}_hashes.jsonl"
        with open(hash_path, "w") as f:
            for h in hashes:
                f.write(json.dumps({"sha256": h}, separators=(",", ":")) + "\n")

        return {
            "category": cat_id,
            "papers_fetched": len(records),
            "jsonl_file": str(jsonl_path.relative_to(self.output_dir.parent)),
            "hash_file": str(hash_path.relative_to(self.output_dir.parent)),
        }

    def materialize_all(self, max_papers_per_category: Optional[int] = None) -> Dict[str, any]:
        """Fetch metadata for all configured categories."""
        categories = self.seed.get("categories", [])
        results = []
        for cat in categories:
            stats = self.materialize_category(cat, max_papers=max_papers_per_category)
            results.append(stats)

        summary = {
            "source": self.seed["root"]["source"],
            "fetch_date": datetime.now(timezone.utc).isoformat(),
            "categories": results,
            "total_papers": sum(r["papers_fetched"] for r in results),
        }
        summary_path = self.output_dir / "materialization_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"Summary written to {summary_path}")
        return summary


def main():
    parser = argparse.ArgumentParser(description="arXiv Metadata Materializer")
    parser.add_argument(
        "--seed",
        default="arxiv_vendor/seed/arxiv_seed.yaml",
        help="Path to arxiv_seed.yaml",
    )
    parser.add_argument(
        "--output-dir",
        default="arxiv_vendor/metadata",
        help="Directory to write JSONL manifests",
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=None,
        help="Maximum papers per category (None = seed default sample)",
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Use default sample size from seed",
    )
    args = parser.parse_args()

    mat = ArxivMaterializer(args.seed, args.output_dir)
    max_papers = args.max_papers
    if args.sample and max_papers is None:
        max_papers = mat.seed.get("fetch", {}).get("default_sample_size", 100)
    summary = mat.materialize_all(max_papers_per_category=max_papers)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

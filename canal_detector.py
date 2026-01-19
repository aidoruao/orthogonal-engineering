import re, json, pathlib, csv, collections

MD_DIR   = pathlib.Path(__file__).parent
# Relaxed Regex: Looks for ANY header containing user/assistant/human/bot, 
# and optionally captures a date/timestamp if present.
CANAL_RE = re.compile(r"^#{1,6}\s+(.*?)\b(user|assistant|human|bot|agent)\b", re.MULTILINE | re.IGNORECASE)
INVAR_RE = re.compile(r"\binvariant\b|\bconstraint\b|\bnever\b|\balways\b|\bmust\b|\bonly\b", re.IGNORECASE)

records = []
# Added a check to ensure we don't crash if no files are found
md_files = list(MD_DIR.glob("*.md"))

for md_file in md_files:
    text = md_file.read_text(encoding="utf8")
    # Find all matches in the file
    matches = list(CANAL_RE.finditer(text))
    
    for i, match in enumerate(matches):
        metadata, role = match.group(1), match.group(2)
        
        # Determine the start and end of the message block
        start_pos = match.end()
        # If there's another header, stop there; otherwise, go 2000 chars or to end of file
        end_limit = matches[i+1].start() if i + 1 < len(matches) else start_pos + 2000
        chunk = text[start_pos:end_limit]
        
        invar = bool(INVAR_RE.search(chunk))
        records.append({
            "file": md_file.stem,
            "info": metadata.strip(), # Captures dates or other header text
            "role": role.lower(),
            "explicit_invariant": invar,
            "canal_candidate": invar and len(chunk.split()) > 5 # Lowered word count threshold
        })

# Prevent DivisionByZero if no records are found
if not records:
    print("No conversation turns found. Check your Markdown header formats.")
else:
    df = collections.defaultdict(list)
    for r in records:
        for k, v in r.items():
            df[k].append(v)

    summary = {
        "total_turns": len(records),
        "canal_candidates": sum(df["canal_candidate"]),
        "explicit_invariants": sum(df["explicit_invariant"]),
        "canal_rate_pct": round(sum(df["canal_candidate"]) / len(records) * 100, 2)
    }

    print(json.dumps(summary, indent=2))
    
    # Save results
    with open(MD_DIR / "universal_inventory.csv", "w", newline='', encoding="utf8") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
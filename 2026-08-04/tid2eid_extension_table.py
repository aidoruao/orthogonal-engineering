#!/usr/bin/env python3
"""tid2eid_extension_table.py — emit the loadable extension table for the frozen hash-MoE.

Consumes the ordered apply-file: each new merge = one new vocab id (V4 vocab = 129,280;
new ids start at 129,280 + order). Expert slot = stable hash of the piece (sha256 % 256),
with the top-100 pieces pinned to distinct experts (catalog #6 resolution; the extension
sim showed hash alone is 1.28× balanced, the pin adds determinism for the head).

Output: tid2eid_extension_v1.jsonl  {new_id, piece, order, eid, pinned}
Verify pass: unique new_ids, eid in 0..255, 100 pinned, max eid load reported.
"""
import hashlib
import json
from pathlib import Path

APPLY = Path(__file__).resolve().parent / "tokenizer_continuation_apply_v1.jsonl"
OUT = Path(__file__).resolve().parent / "tid2eid_extension_v1.jsonl"
VOCAB = 129_280
EXPERTS = 256


def main():
    rows = [json.loads(l) for l in open(APPLY)]
    out_rows = []
    for r in rows:
        order = r["order"]
        new_id = VOCAB + order
        if order < 100:
            eid, pinned = order, True
        else:
            eid = int(hashlib.sha256(r["piece"].encode()).hexdigest(), 16) % EXPERTS
            pinned = False
        out_rows.append({"new_id": new_id, "piece": r["piece"], "order": order,
                         "eid": eid, "pinned": pinned})
    with OUT.open("w") as fh:
        for row in out_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    ids = [r["new_id"] for r in out_rows]
    eids = [r["eid"] for r in out_rows]
    pinned = sum(1 for r in out_rows if r["pinned"])
    from collections import Counter
    load = Counter(eids)
    assert len(set(ids)) == len(ids), "new_id collision"
    assert all(0 <= e < EXPERTS for e in eids), "eid out of range"
    print(f"extension table: {len(out_rows)} entries | new_id range {min(ids)}..{max(ids)} "
          f"| pinned {pinned} | max eid load {max(load.values())} "
          f"(mean {len(out_rows) / EXPERTS:.1f}) | assertions passed")
    print(f"saved: {OUT}")


if __name__ == "__main__":
    main()

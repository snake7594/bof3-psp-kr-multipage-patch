"""Validate that `_ko` can be encoded by the experimental multipage map."""
import json
import os
import re
from collections import Counter

import bof3_encode as Enc


KO_DIR = "_ko"
meta = json.load(open("multipage_map.json", encoding="utf-8"))
cmap = meta["map"]
Enc.LEADS = meta["leads"]
SB = 0xAC00
END = 0xD7A3


def is_hangul(ch):
    return SB <= ord(ch) <= END


def main():
    missing = Counter()
    failures = []
    bodies = 0
    for name in sorted(f for f in os.listdir(KO_DIR) if f.endswith(".txt")):
        for line in open(os.path.join(KO_DIR, name), encoding="utf-8"):
            m = re.match(r"\[[^|]+\|sec(\d+)\|body(\d+)\|[^\]]*\]\s?(.*)", line.rstrip("\n"))
            if not m:
                continue
            bodies += 1
            text = m.group(3)
            text = text.replace("\\n", "\n").replace("{fc}", "")
            for a, t in (("<END>", "\x01"), ("<PAUSE>", "\x02"), ("<BOX>", "\x03")):
                text = text.replace(a, t)
            text = text.replace(">", "")
            for a, t in (("<END>", "\x01"), ("<PAUSE>", "\x02"), ("<BOX>", "\x03")):
                text = text.replace(t, a)
            for ch in text:
                if is_hangul(ch) and ch not in cmap:
                    missing[ch] += 1
            try:
                Enc.encode(text, cmap=cmap)
            except Exception as exc:
                failures.append({"file": name, "sec": int(m.group(1)), "body": int(m.group(2)), "error": str(exc)})

    report = {
        "bodies": bodies,
        "missing_unique": len(missing),
        "missing_occurrences": sum(missing.values()),
        "encode_failures": failures,
        "selected_count": meta["selected_count"],
        "cap": meta["cap"],
    }
    json.dump(report, open("multipage_encoding_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(
        "multipage validation: bodies=%d missing=%d occ=%d encode_failures=%d"
        % (bodies, len(missing), sum(missing.values()), len(failures))
    )


if __name__ == "__main__":
    main()

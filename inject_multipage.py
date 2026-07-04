"""Inject original `_ko` text using the expanded precomposed Hangul map."""
import json
import os
import re
import shutil
import sys

import bof3_encode as Enc
import emi_dialog as E


JPN = "PSP_GAME/USRDIR/JPN"
KO_DIR = "_ko"
BAK = "_emi_bak"
ONLY = sys.argv[1] if len(sys.argv) > 1 else None
meta = json.load(open("multipage_map.json", encoding="utf-8"))
cmap = meta["map"]
Enc.LEADS = meta["leads"]
dedup = json.load(open("_dedup.json", encoding="utf-8"))

_TWO = set(meta["leads"]) | {
    0x04,
    0x05,
    0x07,
    0x0C,
    0x14,
    0x15,
    0x16,
}


def _terminates(by):
    i = 0
    n = len(by)
    while i < n:
        if by[i] == 0x00:
            return True
        i += 2 if by[i] in _TWO else 1
    return False


def relpath_of(txtname):
    return txtname[:-4].replace("_", "/", 1)


def emi_path(txtname):
    return os.path.join(JPN, relpath_of(txtname))


def backup(txtname):
    src = emi_path(txtname)
    dst = os.path.join(BAK, relpath_of(txtname))
    if not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
    return dst


def parse_ko(kof):
    edits = {}
    fails = []
    for line in open(os.path.join(KO_DIR, kof), encoding="utf-8"):
        line = line.rstrip("\n")
        m = re.match(r"\[[^|]+\|sec(\d+)\|body(\d+)\|[^\]]*\]\s?(.*)", line)
        if not m:
            continue
        sec = int(m.group(1))
        bi = int(m.group(2))
        mk = m.group(3)
        mk = mk.replace("\\n", "\n").replace("{fc}", "")
        for a, t in (("<END>", "\x01"), ("<PAUSE>", "\x02"), ("<BOX>", "\x03")):
            mk = mk.replace(a, t)
        mk = mk.replace(">", "")
        for a, t in (("<END>", "\x01"), ("<PAUSE>", "\x02"), ("<BOX>", "\x03")):
            mk = mk.replace(t, a)
        try:
            by = Enc.encode(mk, cmap=cmap)
            if not _terminates(by):
                by = by + b"\x00"
            edits.setdefault(sec, {})[bi] = by
        except Exception as exc:
            fails.append({"file": kof, "sec": sec, "body": bi, "error": str(exc), "text": mk})
    return edits, fails


def inject_member(member_txt, edits):
    bak = backup(member_txt)
    d = open(bak, "rb").read()
    _n, secs = E.parse_toc(d)
    text_secs = {s["idx"] for s in secs if s["ram"] == 0x10000}
    for sec, sedits in edits.items():
        if sec not in text_secs:
            ts_idx = sorted(text_secs)
            if len(ts_idx) == 1:
                sec_use = ts_idx[0]
            else:
                continue
        else:
            sec_use = sec
        d = E.patch_emi(d, sec_use, sedits)
    open(emi_path(member_txt), "wb").write(d)


def main():
    reps = sorted(f for f in os.listdir(KO_DIR) if f.endswith(".txt"))
    if ONLY:
        reps = [r for r in reps if r == ONLY or r == ONLY + ".txt"]
    failures = []
    total_files = 0
    total_bodies = 0
    for kof in reps:
        edits, fails = parse_ko(kof)
        failures.extend(fails)
        total_bodies += sum(len(v) for v in edits.values())
        for member in dedup.get(kof, [kof]):
            inject_member(member, edits)
            total_files += 1
    json.dump(
        failures,
        open("_multipage_inject_failures.json", "w", encoding="utf-8"),
        ensure_ascii=False,
        indent=2,
    )
    print(
        "font-image injected: %d EMI files, %d bodies, %d encode-fails"
        % (total_files, total_bodies, len(failures))
    )


if __name__ == "__main__":
    main()

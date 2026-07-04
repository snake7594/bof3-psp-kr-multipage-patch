"""Build a multi-page precomposed Hangul font-image set for BoF3.

The original path uses only ENDKANJI's native kanji page: 441 cells.  This
path keeps that page and appends two more 256x256 4bpp texture pages to
ENDKANJI.EMI.  A companion EBOOT handler selects the matching texture page and
draws one precomposed 12x12 cell per Hangul syllable.
"""
from collections import Counter
from pathlib import Path
import json
import re
import struct

import numpy as np
from PIL import Image


KO_DIR = Path("_ko")
CAP_PER_PAGE = 441
PAGES = [
    {"name": "endkanji_1e08", "ram": 0x1E080200, "tpage": 0x3F},
    {"name": "extra_0a00", "ram": 0x0A000200, "tpage": 0x25},
    {"name": "extra_0c00", "ram": 0x0C000200, "tpage": 0x26},
]
CAP = CAP_PER_PAGE * len(PAGES)
# 0x20 is kept for the original box/symbol handler, and 0x21 is kept for
# literal '!'.  Six banks are still enough for the 1,147 current syllables.
LEADS = [0x12, 0x13, 0x1E, 0x1F, 0x23, 0x24]
SB = 0xAC00
END = 0xD7A3
CELL = 12
HDR = 0x800
SEC_SIZE = 0x8000
STW = 128
STH = 512
PFP = Path("fonts/mulmaru/MulmaruMono.pfp")
ORIG_FONT = Path("PSP_GAME/USRDIR/JPN/ETC/ENDKANJI.EMI.orig")
FIRST_FONT = Path("PSP_GAME/USRDIR/JPN/ETC/FIRST.EMI")
FIRST_ORIG = Path("PSP_GAME/USRDIR/JPN/ETC/FIRST.EMI.orig")
BATL_RET_FONT = Path("PSP_GAME/USRDIR/JPN/BATTLE/BATL_RET.EMI")
BATL_RET_ORIG = Path("PSP_GAME/USRDIR/JPN/BATTLE/BATL_RET.EMI.orig")


def is_hangul(ch: str) -> bool:
    return SB <= ord(ch) <= END


def stripped(s: str) -> str:
    return re.sub(r"\[[^\]]*\]|\{[^}]*\}|<[^>]*>", "", s)


def collect_menu_syllables() -> list[str]:
    import menu_patch

    seen = set()
    out = []
    for _label, _kind, _primary, _jp, ko, _extra in menu_patch.POOLS:
        for text in ko:
            for ch in text:
                if is_hangul(ch) and ch not in seen:
                    seen.add(ch)
                    out.append(ch)
    return out


def collect_frequency() -> Counter:
    freq = Counter()
    for path in sorted(KO_DIR.glob("*.txt")):
        for ch in stripped(path.read_text(encoding="utf-8")):
            if is_hangul(ch):
                freq[ch] += 1
    return freq


def selected_syllables(freq: Counter) -> list[str]:
    forced = collect_menu_syllables()
    selected = []
    seen = set()
    for ch in forced:
        if ch not in seen:
            selected.append(ch)
            seen.add(ch)
    for ch, _count in freq.most_common():
        if ch not in seen:
            selected.append(ch)
            seen.add(ch)
    if len(selected) > CAP:
        raise RuntimeError(f"multipage font capacity exceeded: {len(selected)} > {CAP}")
    return selected


def pack4(px: np.ndarray) -> bytes:
    flat = px.reshape(-1).astype(np.uint8)
    lo = flat[0::2] & 0xF
    hi = flat[1::2] & 0xF
    return (lo | (hi << 4)).astype(np.uint8).tobytes()


def unpack4(buf: bytes) -> np.ndarray:
    a = np.frombuffer(buf, dtype=np.uint8)
    lo = a & 0xF
    hi = a >> 4
    px = np.empty(a.size * 2, np.uint8)
    px[0::2] = lo
    px[1::2] = hi
    return px.reshape(STH, STW)


def reflow_sec(stored: np.ndarray) -> np.ndarray:
    cv = np.zeros((256, 256), np.uint8)
    for i in range(16):
        cv[(i // 2) * 32 : (i // 2) * 32 + 32, (i % 2) * 128 : (i % 2) * 128 + 128] = stored[
            i * 32 : i * 32 + 32, :
        ]
    return cv


def unreflow_sec(cv: np.ndarray) -> np.ndarray:
    st = np.zeros((STH, STW), np.uint8)
    for i in range(16):
        st[i * 32 : i * 32 + 32, :] = cv[
            (i // 2) * 32 : (i // 2) * 32 + 32, (i % 2) * 128 : (i % 2) * 128 + 128
        ]
    return st


def load_mulmaru_cells():
    data = json.loads(PFP.read_text(encoding="utf-8"))
    by_u = {x["unicode"]: x for x in data["glyphs"]}

    def cell_of(u: int) -> np.ndarray:
        m = np.zeros((CELL, CELL), np.uint8)
        rows = by_u[u].get("data")
        if rows is None:
            return m
        off = CELL - len(rows)
        for r, row in enumerate(rows):
            br = off + r
            if 0 <= br < CELL:
                for c, value in enumerate(row[:CELL]):
                    if value == "#":
                        m[br, c] = 1
        return m

    def syllable_cell(ch: str) -> np.ndarray:
        u = ord(ch)
        glyph = by_u[u]
        if "components" not in glyph:
            return cell_of(u)
        m = np.zeros((CELL, CELL), np.uint8)
        for comp in glyph["components"]:
            m |= cell_of(comp)
        return m

    return syllable_cell


def build_page_cells(selected: list[str]) -> list[np.ndarray]:
    pages = [np.zeros((256, 256), np.uint8) for _ in PAGES]
    syllable_cell = load_mulmaru_cells()
    for slot, ch in enumerate(selected):
        page = slot // CAP_PER_PAGE
        cell = slot % CAP_PER_PAGE
        r = cell // 21
        c = cell % 21
        pages[page][r * CELL : r * CELL + CELL, c * CELL : c * CELL + CELL] = (
            syllable_cell(ch) != 0
        ).astype(np.uint8)
    return pages


def build_emi(page_cvs: list[np.ndarray]) -> bytes:
    orig = bytearray(ORIG_FONT.read_bytes())
    if len(orig) != HDR + SEC_SIZE * 2:
        raise RuntimeError(f"unexpected ENDKANJI size: {len(orig)}")

    out = bytearray(orig[:HDR])
    struct.pack_into("<I", out, 0, 1 + len(page_cvs))

    # Keep ENDKANJI section 0 intact.  The original renderer does not use it for
    # Hangul, but keeping it reduces risk for non-dialog code paths.
    sec0 = bytes(orig[HDR : HDR + SEC_SIZE])
    sections = [(0x1E000200, sec0)]
    for page, cv in zip(PAGES, page_cvs):
        sections.append((page["ram"], pack4(unreflow_sec(cv))))

    for i, (ram, blob) in enumerate(sections, start=1):
        first4 = struct.unpack_from("<I", blob, 0)[0]
        struct.pack_into("<IIIH2s", out, i * 16, len(blob), ram, first4, 3, b"..")

    for _ram, blob in sections:
        out += blob
    return bytes(out)


def align800(n: int) -> int:
    return (n + 0x7FF) & ~0x7FF


def patch_aux_font(src: Path, out_path: Path, page_blobs: list[bytes]) -> None:
    """Patch font-bearing EMI files that load the same texture pages as ENDKANJI."""
    data = bytearray(src.read_bytes())
    count = struct.unpack_from("<I", data, 0)[0]
    starts = {}
    pos = HDR
    for i in range(1, count + 1):
        size, ram, _first4, kind, _dots = struct.unpack_from("<IIIH2s", data, i * 16)
        pos = align800(pos)
        starts[ram] = (i, pos, size, kind)
        pos += size

    for page, blob in zip(PAGES, page_blobs):
        ram = page["ram"]
        if ram in starts:
            idx, off, size, kind = starts[ram]
            if size != SEC_SIZE:
                raise RuntimeError(f"{src}: section {idx} has unexpected size {size:#x}")
            data[off : off + SEC_SIZE] = blob
            first4 = struct.unpack_from("<I", blob, 0)[0]
            struct.pack_into("<IIIH2s", data, idx * 16, SEC_SIZE, ram, first4, kind, b"..")
            continue

        count += 1
        header_off = count * 16
        if header_off + 16 > HDR:
            raise RuntimeError(f"{src}: no room for extra section header")
        off = align800(len(data))
        if len(data) < off:
            data += b"\x00" * (off - len(data))
        first4 = struct.unpack_from("<I", blob, 0)[0]
        struct.pack_into("<IIIH2s", data, header_off, SEC_SIZE, ram, first4, 3, b"..")
        data += blob

    struct.pack_into("<I", data, 0, count)
    out_path.write_bytes(data)


def save_preview(page_cvs: list[np.ndarray]) -> None:
    scale = 3
    pad = 18
    w = 256 * scale * len(page_cvs) + pad * (len(page_cvs) + 1)
    h = 256 * scale + pad * 2
    img = Image.new("RGB", (w, h), (28, 28, 32))
    for i, cv in enumerate(page_cvs):
        sub = Image.fromarray((cv > 0).astype(np.uint8) * 255, "L").resize(
            (256 * scale, 256 * scale), Image.Resampling.NEAREST
        )
        img.paste(sub.convert("RGB"), (pad + i * (256 * scale + pad), pad))
    img.save("multipage_font_preview.png")


def token_for_slot(slot: int) -> list[int]:
    return [LEADS[slot // 256], slot % 256]


def main():
    if not ORIG_FONT.exists():
        raise FileNotFoundError(f"missing original font: {ORIG_FONT}")
    freq = collect_frequency()
    selected = selected_syllables(freq)
    selected_set = set(selected)
    overflow = [(ch, c) for ch, c in freq.most_common() if ch not in selected_set]
    page_cvs = build_page_cells(selected)
    page_blobs = [pack4(unreflow_sec(cv)) for cv in page_cvs]
    Path("ENDKANJI_multipage.EMI").write_bytes(build_emi(page_cvs))
    patch_aux_font(FIRST_ORIG if FIRST_ORIG.exists() else FIRST_FONT, Path("FIRST_fontimage.EMI"), page_blobs)
    patch_aux_font(BATL_RET_ORIG if BATL_RET_ORIG.exists() else BATL_RET_FONT, Path("BATL_RET_fontimage.EMI"), page_blobs)
    save_preview(page_cvs)

    cmap = {ch: slot for slot, ch in enumerate(selected)}
    report = {
        "ko_dir": str(KO_DIR),
        "cap_per_page": CAP_PER_PAGE,
        "page_count": len(PAGES),
        "cap": CAP,
        "leads": LEADS,
        "pages": PAGES,
        "selected_count": len(selected),
        "source_unique": len(freq),
        "source_total": sum(freq.values()),
        "covered_occurrences": sum(freq[ch] for ch in selected_set if ch in freq),
        "overflow_unique": len(overflow),
        "overflow_occurrences": sum(c for _ch, c in overflow),
        "coverage": sum(freq[ch] for ch in selected_set if ch in freq) / max(1, sum(freq.values())),
        "map": cmap,
        "tokens": {ch: token_for_slot(slot) for ch, slot in cmap.items()},
        "overflow_syllables": [{"syllable": ch, "count": c} for ch, c in overflow],
    }
    Path("multipage_map.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        "multipage font: selected=%d unique=%d overflow=%d occ=%d coverage=%.4f"
        % (
            len(selected),
            len(freq),
            len(overflow),
            sum(c for _ch, c in overflow),
            report["coverage"],
        )
    )


if __name__ == "__main__":
    main()

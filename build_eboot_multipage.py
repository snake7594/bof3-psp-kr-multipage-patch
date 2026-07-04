"""Build an EBOOT with a multi-page precomposed Hangul font-image handler."""
import json
import struct
from pathlib import Path

import bof3_encode as Enc
import menu_patch


SRC = Path("PSP_GAME/SYSDIR/BOOT.BIN.orig")
OUT = Path("BOOT_multipage.BIN")
MAP = Path("multipage_map.json")
HV = 0x373670
INS_FOFF = 0x3736F0
SEG1_VA = 0x373670
JT = 0x2D0BE8

R = {
    "zero": 0,
    "at": 1,
    "v0": 2,
    "v1": 3,
    "a0": 4,
    "a1": 5,
    "a2": 6,
    "a3": 7,
    "t0": 8,
    "t1": 9,
    "t2": 10,
    "t3": 11,
    "t4": 12,
    "t5": 13,
    "t6": 14,
    "t7": 15,
    "s0": 16,
    "s1": 17,
    "s2": 18,
    "s3": 19,
    "s4": 20,
    "s5": 21,
    "s6": 22,
    "s7": 23,
    "t8": 24,
    "t9": 25,
    "sp": 29,
    "fp": 30,
    "ra": 31,
}


def _r(x):
    return R[x] if isinstance(x, str) else x


def itype(op, rs, rt, imm):
    return (op << 26) | (_r(rs) << 21) | (_r(rt) << 16) | (imm & 0xFFFF)


def rtype(rs, rt, rd, sh, fn):
    return (_r(rs) << 21) | (_r(rt) << 16) | (_r(rd) << 11) | (sh << 6) | fn


prog = []


def e(kind, *args, c=""):
    prog.append([kind, list(args), c])


def enc(kind, args, cur, labels):
    if kind == "bal":
        off = ((cur + 8) - (cur + 4)) >> 2
        return (0x01 << 26) | (0x11 << 16) | (off & 0xFFFF)
    if kind == "nop":
        return 0
    if kind == "lui":
        return itype(0x0F, 0, args[0], args[1])
    if kind == "ori":
        return itype(0x0D, args[1], args[0], args[2])
    if kind == "andi":
        return itype(0x0C, args[1], args[0], args[2])
    if kind == "addiu":
        return itype(0x09, args[1], args[0], args[2])
    if kind == "addu":
        return rtype(args[1], args[2], args[0], 0, 0x21)
    if kind == "subu":
        return rtype(args[1], args[2], args[0], 0, 0x23)
    if kind == "move":
        return rtype(args[1], 0, args[0], 0, 0x21)
    if kind == "sll":
        return rtype(0, args[1], args[0], args[2], 0x00)
    if kind == "srl":
        return rtype(0, args[1], args[0], args[2], 0x02)
    if kind == "lw":
        return itype(0x23, args[2], args[0], args[1])
    if kind == "sw":
        return itype(0x2B, args[2], args[0], args[1])
    if kind == "lh":
        return itype(0x21, args[2], args[0], args[1])
    if kind == "sh":
        return itype(0x29, args[2], args[0], args[1])
    if kind == "lbu":
        return itype(0x24, args[2], args[0], args[1])
    if kind == "lhu":
        return itype(0x25, args[2], args[0], args[1])
    if kind == "sb":
        return itype(0x28, args[2], args[0], args[1])
    if kind == "div":
        return rtype(args[0], args[1], 0, 0, 0x1A)
    if kind == "mflo":
        return rtype(0, 0, args[0], 0, 0x12)
    if kind == "mfhi":
        return rtype(0, 0, args[0], 0, 0x10)
    if kind == "jalr":
        return rtype(args[0], 0, "ra", 0, 0x09)
    if kind == "jr":
        return rtype(args[0], 0, 0, 0, 0x08)
    if kind == "LABEL":
        return None
    raise ValueError(kind)


def load_seg0_offset(reg, offset):
    e("lw", "t8", 0x10, "sp")
    e("lui", reg, (offset >> 16) & 0xFFFF)
    e("ori", reg, reg, offset & 0xFFFF)
    e("addu", "t9", "t8", reg)


def emit_select_tpage(reg):
    e("lw", "t3", 0x14, "sp")
    e("lui", "t1", 0x000D)
    e("ori", "t1", "t1", 0x07D0)
    e("addu", "t1", "t3", "t1")
    e("lw", "a0", 0, "t1")
    e("move", "a1", "zero")
    e("move", "a2", "zero")
    e("move", "a3", reg)
    load_seg0_offset("t1", 0x9FD54)
    e("jalr", "t9")
    e("move", "t0", "zero")
    load_seg0_offset("t1", 0x3740)
    e("ori", "a0", "zero", 1)
    e("jalr", "t9")
    e("ori", "a1", "zero", 0x10)


def emit_draw_cell():
    e("lw", "t6", 0, "sp")
    e("ori", "t7", "zero", 0x15)
    e("div", "t6", "t7")
    e("mflo", "t5")
    e("mfhi", "t6")
    e("addu", "t8", "t6", "t6")
    e("addu", "t6", "t6", "t8")
    e("sll", "t6", "t6", 2)
    e("addu", "t8", "t5", "t5")
    e("addu", "t5", "t5", "t8")
    e("sll", "t5", "t5", 2)
    e("addu", "t5", "t5", "s4")
    e("lw", "t3", 0x14, "sp")
    e("lui", "t1", 0x000D)
    e("ori", "t1", "t1", 0x07D0)
    e("addu", "t1", "t3", "t1")
    e("lw", "t4", 0, "t1")
    e("sb", "t6", 0x0C, "t4")
    e("sb", "t5", 0x0D, "t4")
    e("ori", "t9", "zero", 0x0C)
    e("sh", "t9", 0x10, "t4")
    e("lw", "t9", 0x24, "sp")
    e("sh", "t9", 0x12, "t4")
    e("lui", "t1", 0x0010)
    e("ori", "t1", "t1", 0x7750)
    e("addu", "t1", "t3", "t1")
    e("lh", "a0", 0, "t1")
    e("lui", "t1", 0x0010)
    e("ori", "t1", "t1", 0x7790)
    e("addu", "t1", "t3", "t1")
    e("lh", "a1", 0, "t1")
    e("move", "a2", "fp")
    e("move", "a3", "s4")
    e("lw", "t8", 0x10, "sp")
    e("ori", "t1", "zero", 0x955C)
    e("addu", "t9", "t8", "t1")
    e("jalr", "t9")
    e("nop")


# Prologue: derive relocation bases.
e("bal")
e("nop")
e("lui", "t1", 0x0037)
e("ori", "t1", "t1", 0x3678)
e("subu", "t0", "ra", "t1")
e("sw", "t0", 0x10, "sp")
e("lw", "t2", 0x30, "sp")
e("lui", "t3", 0x0010)
e("ori", "t3", "t3", 0xA250)
e("subu", "t3", "t2", "t3")
e("sw", "t3", 0x14, "sp")

# glyph_idx = banktbl[lead - 0x12] * 256 + next_byte
e("lbu", "t5", 0, "s3")
e("addiu", "s3", "s3", 1)
e("lbu", "a1", 0, "s0")
e("addiu", "a1", "a1", -0x12)
e("lw", "t0", 0x10, "sp")
e("lui", "t1", 0, c="hi(BANKTBL_VA)")
e("ori", "t1", "t1", 0, c="lo(BANKTBL_VA)")
e("addu", "t1", "t0", "t1")
e("addu", "t1", "t1", "a1")
e("lbu", "a2", 0, "t1")
e("sll", "a2", "a2", 8)
e("addu", "t5", "t5", "a2")

# entry = glyph_table[idx], low 9 bits = cell, high bits = page index.
e("lw", "t0", 0x10, "sp")
e("lui", "t1", 0, c="hi(GLYPHTBL_VA)")
e("ori", "t1", "t1", 0, c="lo(GLYPHTBL_VA)")
e("addu", "t1", "t0", "t1")
e("sll", "t5", "t5", 1)
e("addu", "t1", "t1", "t5")
e("lhu", "t6", 0, "t1")
e("andi", "t7", "t6", 0x01FF)
e("sw", "t7", 0, "sp")
e("srl", "t6", "t6", 9)
e("lui", "t1", 0, c="hi(PAGETBL_VA)")
e("ori", "t1", "t1", 0, c="lo(PAGETBL_VA)")
e("addu", "t1", "t0", "t1")
e("addu", "t1", "t1", "t6")
e("lbu", "t7", 0, "t1")
e("sw", "t7", 4, "sp")

e("lw", "t7", 4, "sp")
emit_select_tpage("t7")
emit_draw_cell()

# Restore the regular FIRST page after each custom glyph.  This avoids stale
# page-latch state when punctuation, ASCII, or the original 0x20 handler follows.
e("ori", "t7", "zero", 0x2F)
emit_select_tpage("t7")
e("lw", "t3", 0x14, "sp")
e("lui", "t4", 0x0010)
e("ori", "t4", "t4", 0x7810)
e("addu", "t4", "t3", "t4")
e("sb", "zero", 0, "t4")

e("lw", "t3", 0x14, "sp")
e("lui", "t1", 0x0010)
e("ori", "t1", "t1", 0x7750)
e("addu", "t1", "t3", "t1")
e("lh", "a0", 0, "t1")
e("addiu", "a0", "a0", 0x0C)
e("sh", "a0", 0, "t1")
e("lw", "t8", 0x10, "sp")
e("ori", "t1", "zero", 0x9FF0)
e("addu", "t9", "t8", "t1")
e("jr", "t9")
e("nop")


def assemble(banktbl_va, pagetbl_va, glyphtbl_va):
    labels = {}
    addr = HV
    for kind, args, _c in prog:
        if kind == "LABEL":
            labels[args[0]] = addr
        else:
            addr += 4
    words = []
    addr = HV
    for kind, args, c in prog:
        if kind == "LABEL":
            continue
        aa = list(args)
        if kind == "lui" and "hi(BANKTBL_VA)" in c:
            aa = [aa[0], (banktbl_va >> 16) & 0xFFFF]
        if kind == "ori" and "lo(BANKTBL_VA)" in c:
            aa = [aa[0], aa[1], banktbl_va & 0xFFFF]
        if kind == "lui" and "hi(PAGETBL_VA)" in c:
            aa = [aa[0], (pagetbl_va >> 16) & 0xFFFF]
        if kind == "ori" and "lo(PAGETBL_VA)" in c:
            aa = [aa[0], aa[1], pagetbl_va & 0xFFFF]
        if kind == "lui" and "hi(GLYPHTBL_VA)" in c:
            aa = [aa[0], (glyphtbl_va >> 16) & 0xFFFF]
        if kind == "ori" and "lo(GLYPHTBL_VA)" in c:
            aa = [aa[0], aa[1], glyphtbl_va & 0xFFFF]
        words.append(enc(kind, aa, addr, labels))
        addr += 4
    return b"".join(struct.pack("<I", w) for w in words)


def align16(n):
    return (n + 15) & ~15


def main():
    meta = json.loads(MAP.read_text(encoding="utf-8"))
    leads = meta["leads"]
    pages = meta["pages"]
    Enc.LEADS = leads
    menu_patch.Enc.LEADS = leads
    menu_patch.CMAP = meta["map"]

    banktbl = bytearray(max(leads) - 0x12 + 1)
    for bank, lead in enumerate(leads):
        banktbl[lead - 0x12] = bank
    pagetbl = bytes(page["tpage"] for page in pages)

    entry_count = len(leads) * 256
    glyph_entries = [0] * entry_count
    for slot in range(meta["selected_count"]):
        page = slot // 441
        cell = slot % 441
        glyph_entries[slot] = (page << 9) | cell
    glyphtbl = b"".join(struct.pack("<H", x) for x in glyph_entries)

    hlen = sum(1 for kind, _args, _c in prog if kind != "LABEL") * 4
    handler_pad = align16(hlen)
    banktbl_va = HV + handler_pad
    banktbl_pad = align16(len(banktbl))
    pagetbl_va = banktbl_va + banktbl_pad
    pagetbl_pad = align16(len(pagetbl))
    glyphtbl_va = pagetbl_va + pagetbl_pad
    handler = assemble(banktbl_va, pagetbl_va, glyphtbl_va)
    assert len(handler) == hlen

    region = bytearray(handler)
    region += b"\x00" * (handler_pad - len(region))
    region += banktbl + b"\x00" * (banktbl_pad - len(banktbl))
    region += pagetbl + b"\x00" * (pagetbl_pad - len(pagetbl))
    region += glyphtbl
    grow = (len(region) + 0x3F) & ~0x3F
    region += b"\x00" * (grow - len(region))

    print(
        "handler=%#x banktbl=%#x pagetbl=%#x glyphtbl=%#x grow=%#x"
        % (hlen, len(banktbl), len(pagetbl), len(glyphtbl), grow)
    )

    b = bytearray(SRC.read_bytes())
    print(menu_patch.patch_menus(b))
    b[INS_FOFF:INS_FOFF] = region

    e_shoff = struct.unpack_from("<I", b, 0x20)[0]
    if e_shoff >= INS_FOFF:
        struct.pack_into("<I", b, 0x20, e_shoff + grow)
    e_phoff = struct.unpack_from("<I", b, 0x1C)[0]
    e_phnum = struct.unpack_from("<H", b, 0x2C)[0]
    for i in range(e_phnum):
        o = e_phoff + i * 32
        p_type, p_off, p_va, p_pa, p_fsz, p_msz, p_flags, p_align = struct.unpack_from(
            "<IIIIIIII", b, o
        )
        if i == 0:
            p_fsz += grow
            p_msz += grow
        else:
            if p_off >= INS_FOFF:
                p_off += grow
            if p_va >= SEG1_VA:
                p_va += grow
        struct.pack_into("<IIIIIIII", b, o, p_type, p_off, p_va, p_pa, p_fsz, p_msz, p_flags, p_align)

    new_shoff = struct.unpack_from("<I", b, 0x20)[0]
    e_shnum = struct.unpack_from("<H", b, 0x30)[0]
    for i in range(e_shnum):
        o = new_shoff + i * 40
        sh_name, sh_type, sh_flags, sh_addr, sh_off, sh_size, sh_link, sh_info, sh_align, sh_entsz = struct.unpack_from(
            "<IIIIIIIIII", b, o
        )
        if sh_off >= INS_FOFF:
            sh_off += grow
        if sh_addr >= SEG1_VA:
            sh_addr += grow
        struct.pack_into(
            "<IIIIIIIIII",
            b,
            o,
            sh_name,
            sh_type,
            sh_flags,
            sh_addr,
            sh_off,
            sh_size,
            sh_link,
            sh_info,
            sh_align,
            sh_entsz,
        )

    for lead in leads:
        struct.pack_into("<I", b, JT + lead * 4, HV)
    b += b"\x00" * 0x40
    OUT.write_bytes(b)
    print("wrote", OUT, len(b), "bytes")


if __name__ == "__main__":
    main()

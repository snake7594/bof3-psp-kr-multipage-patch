"""Apply final byte-level fixes found in the prior BoF3 analysis tree.

These two files were not touched by the automated dialog/font/EBOOT pipeline,
but the prior final PSP_GAME has small confirmed byte edits:
- BATTLE/BATTLE2.EMI: 3 bytes
- ETC/AFLDKWA.EMI: 9 bytes

The script verifies the clean ISO bytes before writing, so it is safe to rerun.
"""
from pathlib import Path


PATCHES = [
    (
        Path("PSP_GAME/USRDIR/JPN/BATTLE/BATTLE2.EMI"),
        0x05CA69,
        bytes.fromhex("3a 12 88"),
        bytes.fromhex("00 f5 00"),
    ),
    (
        Path("PSP_GAME/USRDIR/JPN/ETC/AFLDKWA.EMI"),
        0x0018FB,
        bytes.fromhex("ad fc d3 af d3 12 6b 12 5b"),
        bytes.fromhex("12 1d c0 12 19 ed 12 0e 85"),
    ),
]


def main():
    for rel, off, before, after in PATCHES:
        data = bytearray(rel.read_bytes())
        cur = bytes(data[off : off + len(before)])
        if cur == after:
            print(f"{rel}: already patched")
            continue
        if cur != before:
            raise RuntimeError(
                f"{rel}: unexpected bytes at 0x{off:x}: "
                f"got {cur.hex(' ')}, expected {before.hex(' ')}"
            )
        data[off : off + len(before)] = after
        rel.write_bytes(data)
        print(f"{rel}: patched {len(before)} bytes at 0x{off:x}")


if __name__ == "__main__":
    main()

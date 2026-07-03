# BOF3 Korean Patch Preparation

## Source

- Clean ISO: `C:\Users\Jae Ho Lee\Pictures\psp\roms\BOF3\Breath of Fire III.iso`
- ISO size: `403,963,904` bytes
- ISO SHA-256: `861C0209A0E2702928A7DECE3C0351C4A9675135AA94BB473A6ABAD24462DCD6`
- Prior analysis tree: `C:\Users\Jae Ho Lee\Pictures\psp\roms\Breath of Fire III`

## Prepared Working Tree

- Patch tree: `C:\Users\Jae Ho Lee\Documents\Codex\2026-07-03\c-users-jae-ho-lee-pictures\work\bof3_patch_prep\patch_tree`
- ISO extraction: `1,846` files, `343,535,569` bytes of file payload
- Translation assets copied: `_ko`, font assets, codec/injection/build scripts, compact maps/tables

## Applied Steps

1. Extracted the clean ISO with `pycdlib`.
2. Copied the existing Korean patch toolchain and translation assets from the prior analysis tree.
3. Created clean `BOOT.BIN.orig` and `EBOOT.BIN.orig` from the ISO extraction.
4. Ran `python inject_all.py`.
   - Result: `199` EMI files injected, `7,799` bodies, `0` encode failures.
5. Ran `python build_eboot.py`.
   - Result: `BOOT_mulmaru.BIN`, `5,086,709` bytes.
   - Menu pools patched: main menu `4`, sort `1`, battle command `1`, status `5`.
6. Deployed generated/reused assets:
   - `BOOT_mulmaru.BIN` -> `PSP_GAME\SYSDIR\EBOOT.BIN`
   - `ENDKANJI_mulmaru.EMI` -> `PSP_GAME\USRDIR\JPN\ETC\ENDKANJI.EMI`
   - `FIRST_mulmaru.EMI` -> `PSP_GAME\USRDIR\JPN\ETC\FIRST.EMI`
   - `BATL_RET_mulmaru.EMI` -> `PSP_GAME\USRDIR\JPN\BATTLE\BATL_RET.EMI`
7. Added and ran `apply_manual_final_diffs.py` for the two small final-state byte edits missing from the automated pipeline:
   - `BATTLE\BATTLE2.EMI` at `0x05CA69`, 3 bytes
   - `ETC\AFLDKWA.EMI` at `0x0018FB`, 9 bytes

## Verification

- Compared the prepared `PSP_GAME` against the prior final patched `PSP_GAME`.
- Excluded only backup files that exist in the old tree: `*.EMI.orig`, `BOOT.BIN.orig`, `EBOOT.BIN.orig`.
- Result: `1,845 / 1,845` files matched, `0` missing, `0` extra, `0` hash differences.

## Notes

- The clean ISO was not modified.
- A rebuilt patched ISO was not generated in this step; the prepared output is a patched `PSP_GAME` tree plus reproducible scripts.
- Existing text/menu logs contain mojibake in several notes, but this preparation mirrors the prior final patched binary state exactly.

# BoF3 multipage Hangul font experiment

## Result

- Experimental multipage path built and deployed into the working `PSP_GAME` tree.
- Current `_ko` translation fits without lossy substitution.
- Hangul syllables selected: 1,147 / 1,147
- Font capacity: 1,323 cells = 441 cells x 3 texture pages
- Overflow: 0 unique syllables, 0 occurrences
- Encoded dialog bodies: 7,799
- Encode failures: 0
- Injected EMI files: 199

## Files in patch tree

- `BOOT_multipage.BIN`
- `ENDKANJI_multipage.EMI`
- `multipage_map.json`
- `multipage_encoding_report.json`
- `multipage_font_preview.png`
- `build_multipage_font.py`
- `build_eboot_multipage.py`
- `inject_multipage.py`
- `validate_multipage_encoding.py`
- `build_multipage_pipeline.py`

## Deployed files

- `PSP_GAME/SYSDIR/EBOOT.BIN`
  - Size: 5,081,397 bytes
  - SHA256: `0015A901D618341C8F43C08708E337A2DECE4D353F8BCB89D5A4999A757924B3`
- `PSP_GAME/USRDIR/JPN/ETC/ENDKANJI.EMI`
  - Size: 133,120 bytes
  - SHA256: `498DA59B249439EC6CC92CED7B35CBF21DB5FA5D14446B2B4F180F6C2E95986B`

## Encoding

The new handler uses these two-byte lead banks:

- `0x12`
- `0x13`
- `0x1e`
- `0x1f`
- `0x23`
- `0x24`

The following bytes were deliberately preserved:

- `0x20`: original handler, to avoid box/symbol conflict
- `0x21`: literal `!`, because `_ko` contains a real exclamation mark

Post-injection scan:

- Invalid Hangul lead slots: 0
- Literal source conflicts with active lead bytes: 0
- Raw `0x20` count in text sections: 4
- Raw `0x21` count in text sections: 3

## ENDKANJI layout

`ENDKANJI.EMI` was expanded from 2 sections to 4 sections:

| Section | Size | RAM tag | Texture page |
|---:|---:|---:|---:|
| 0 | `0x8000` | `0x1e000200` | original preserved |
| 1 | `0x8000` | `0x1e080200` | `0x3f` |
| 2 | `0x8000` | `0x0a000200` | `0x25` |
| 3 | `0x8000` | `0x0c000200` | `0x26` |

## EBOOT handler

The jump table now routes these bytes to the new handler at `0x373670`:

- `0x12`, `0x13`, `0x1e`, `0x1f`, `0x23`, `0x24`

The new handler:

1. Reads `lead + index`.
2. Converts it to a compact Hangul slot.
3. Looks up the target texture page and 12x12 cell.
4. Selects the texture page directly.
5. Draws the cell through the game's original sprite draw function.
6. Restores the regular FIRST page afterward.

## Caveat

This is statically validated but not yet runtime-verified in PPSSPP/PSP. The remaining risk is whether the added ENDKANJI sections at RAM tags `0x0a000200` and `0x0c000200` are loaded and sampled exactly as expected during live rendering.

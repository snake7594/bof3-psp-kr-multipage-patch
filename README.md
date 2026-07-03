# Breath of Fire III PSP Korean patch tools

Experimental Korean patch preparation for the PSP version of **Breath of Fire III**.

This repository contains the current multipage precomposed-Hangul patch workflow:

- 1,147 Hangul syllables from the current Korean script fit without lossy substitution.
- The experimental font capacity is 1,323 cells, using three 441-cell texture pages.
- The EBOOT handler routes six two-byte lead banks to the new multipage renderer.
- Static validation currently passes for 7,799 dialog bodies with 0 encode failures.

## Important

This repository does not include original game files, ISO images, or modified game binaries.

To use the patch, you must provide your own legally obtained PSP game files and extract them
into a working folder that contains `PSP_GAME`.

## Apply The Current Patch

1. Install Python 3.12 or newer.
2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Copy or clone this repository into a clean extracted game folder, so this file and
   `PSP_GAME` are in the same directory.
4. Run:

```powershell
python run_multipage_patch.py
```

The script will:

- preserve clean originals as `.orig` files when needed,
- build the 1,147-syllable multipage font,
- build the experimental EBOOT handler,
- inject the Korean script into EMI files,
- apply the two confirmed byte-level fixes from prior analysis.

## Generated Files

After a successful run, the working tree will contain:

- `PSP_GAME/SYSDIR/EBOOT.BIN`
- `PSP_GAME/USRDIR/JPN/ETC/ENDKANJI.EMI`
- translated dialog EMI files under `PSP_GAME/USRDIR/JPN`
- `multipage_map.json`
- `multipage_encoding_report.json`
- `multipage_font_preview.png`

## Runtime Status

The patch is statically validated, but the new `0x25` and `0x26` texture pages still need
runtime verification in PPSSPP or on PSP hardware.

## Included Font

The patch builder uses Mulmaru Mono source data under the SIL Open Font License 1.1.
See `fonts/mulmaru/LICENSE.txt`.

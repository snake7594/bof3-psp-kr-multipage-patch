# BOF3 Precomposed Hangul Font Progress

## Direction

- Replaced the johab-first approach with a stable 441-slot precomposed Hangul path.
- The path uses the game's native kanji renderer for `0x12/0x13` tokens.
- No custom johab composition handler is installed in the precomposed EBOOT.

## Current Working Tree

- Patch tree: `C:\Users\Jae Ho Lee\Documents\Codex\2026-07-03\c-users-jae-ho-lee-pictures\work\bof3_patch_prep\patch_tree`
- Main reproducible command:
  - `python build_precomposed_pipeline.py`

## Added Pipeline Files

- `reduce_ko_syllables.py`
  - Builds `_ko_reduced` from `_ko`.
  - Applies conservative wording substitutions for rare syllables.
- `build_precomposed_font.py`
  - Builds `precomposed_map.json`.
  - Bakes 441 full Mulmaru Hangul syllables into `ENDKANJI_precomposed.EMI`.
- `make_precomposed_ko.py`
  - Builds `_ko_precomposed`.
  - Replaces remaining out-of-budget syllables with closest mapped syllables for a complete test build.
- `validate_precomposed_encoding.py`
  - Verifies `_ko_precomposed` has no syllables outside the 441-slot map.
- `build_eboot_precomposed.py`
  - Patches executable menu text only.
  - Leaves original kanji/twin-kanji jump table intact.
- `inject_precomposed.py`
  - Injects `_ko_precomposed` into EMI text sections with pointer recalculation.
- `build_precomposed_pipeline.py`
  - Runs the full sequence and deploys the precomposed assets into `PSP_GAME`.

## Current Results

- `_ko_reduced`
  - Replacements: `2,363`
  - Unique syllables after conservative pass: `1,111`
  - 441-slot overflow after conservative pass: `670` syllables / `4,543` occurrences
- `_ko_precomposed`
  - Automatic rare-syllable substitutions: `4,856`
  - Final unique syllables: `441`
  - Encoding missing syllables: `0`
- Injection
  - EMI files injected: `199`
  - Bodies injected: `7,799`
  - Encode failures: `0`
- EBOOT
  - `0x12/0x13/0x1e/0x1f/0x20/0x21/0x23/0x24` jump-table entries match original `BOOT.BIN.orig`.
  - `EBOOT.BIN` SHA-256: `F967CA3907A113559CCFB18564BDECF5A810E44A78F3BFA8A48657CCE44E18A3`
- Font
  - `ENDKANJI.EMI` SHA-256: `0F5BA4E505BF05FE2CC0197AC6E7A2FE67A49C4C8669B4EBA46978F43E2224E1`

## Notes

- `_ko_precomposed` is a complete playable test-build text set, but it contains lossy automatic substitutions. It should be reviewed and refined over time.
- `_ko_reduced` is the safer human-readable reduction layer and should be the base for future manual cleanup.
- A rebuilt ISO has not been generated in this step.

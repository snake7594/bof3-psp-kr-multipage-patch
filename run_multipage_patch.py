"""Prepare clean files and run the current BoF3 PSP Korean multipage patch."""
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
PSP_GAME = ROOT / "PSP_GAME"


def require(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"missing required path: {path}")


def preserve(src: Path, dst: Path) -> None:
    if dst.exists():
        return
    require(src)
    shutil.copy2(src, dst)
    print(f"preserved {dst.relative_to(ROOT)}")


def run(script: str) -> None:
    print(f"> {script}")
    subprocess.check_call([sys.executable, script], cwd=ROOT)


def main() -> None:
    require(PSP_GAME)
    preserve(PSP_GAME / "SYSDIR" / "BOOT.BIN", PSP_GAME / "SYSDIR" / "BOOT.BIN.orig")
    if (PSP_GAME / "SYSDIR" / "EBOOT.BIN").exists():
        preserve(PSP_GAME / "SYSDIR" / "EBOOT.BIN", PSP_GAME / "SYSDIR" / "EBOOT.BIN.orig")
    preserve(
        PSP_GAME / "USRDIR" / "JPN" / "ETC" / "ENDKANJI.EMI",
        PSP_GAME / "USRDIR" / "JPN" / "ETC" / "ENDKANJI.EMI.orig",
    )
    run("build_multipage_pipeline.py")


if __name__ == "__main__":
    main()

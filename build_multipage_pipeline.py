"""Run the experimental multipage precomposed-font pipeline."""
import shutil
import subprocess
import sys
from pathlib import Path


def run(args):
    print(">", " ".join(args))
    subprocess.check_call([sys.executable] + args)


def main():
    run(["build_multipage_font.py"])
    run(["validate_multipage_encoding.py"])
    run(["build_eboot_multipage.py"])

    shutil.copy("BOOT_multipage.BIN", "PSP_GAME/SYSDIR/EBOOT.BIN")
    shutil.copy("ENDKANJI_multipage.EMI", "PSP_GAME/USRDIR/JPN/ETC/ENDKANJI.EMI")
    run(["inject_multipage.py"])
    if Path("apply_manual_final_diffs.py").exists():
        run(["apply_manual_final_diffs.py"])
    print("multipage pipeline complete")


if __name__ == "__main__":
    main()

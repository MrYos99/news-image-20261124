#!/usr/bin/env python3
"""Entry point for the news-image-20261124 bounty.

Renders Tuesday 24 November 2026's world news as a single 1024x1024
newspaper front page and writes it to /output/entry.png.

Stdlib only. The image is produced by render.py (Pillow is a declared
runtime dependency of that module); this entry point copies the bytes
render.py writes so the arena output is exactly the image verified
locally. No network access, no randomness, no timestamps.
"""

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    subprocess.run([sys.executable, os.path.join(HERE, "render.py")],
                   check=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst, os.path.getsize(dst), "bytes")


if __name__ == "__main__":
    main()

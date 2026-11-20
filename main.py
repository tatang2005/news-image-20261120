"""Entry point for the news-image-20261120 make.fun submission.

Renders the front page with draw.py (pure standard library) and writes
entry.png next to this file; if an output directory is available
($MAKEFUN_OUTPUT_DIR, default /output) the PNG is written there too.
"""

import os

import draw


def main():
    page = draw.build_front_page()

    here = os.path.dirname(os.path.abspath(__file__))
    local_path = os.path.join(here, "entry.png")
    page.save(local_path)
    print("wrote", local_path)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "entry.png")
        page.save(out_path)
        print("wrote", out_path)
    except OSError as exc:
        print("output dir skipped:", exc)


if __name__ == "__main__":
    main()

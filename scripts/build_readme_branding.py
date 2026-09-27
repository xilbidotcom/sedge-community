# Copyright 2026 Xilbi Sistemas de Informacion SL
# SPDX-License-Identifier: Apache-2.0
"""Wrap unchanged logo PNGs in self-contained, theme-independent SVG panels.

Only README presentation files are written. The application artwork is neither
edited nor re-encoded. Run --check to detect stale panels without writing files.
"""

import argparse
import base64
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
PANELS = (
    ("sedge-logo", "SEDGE", 320),
    ("xilbi", "XILBI", 256),
    ("eu-funding", "Funded by the European Union", 352),
    ("o-cei-logo", "O-CEI", 128),
)


def render(name, title, width):
    """Embed the original bytes; the opaque rectangle supplies the contrast."""
    payload = base64.b64encode((ROOT / "web/public/brand" / f"{name}.png").read_bytes()).decode("ascii")
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="112" viewBox="0 0 {width} 112" '
        'role="img" aria-labelledby="title">\n'
        '  <!-- Presentation wrapper; artwork terms remain in BRANDING.md. -->\n'
        f'  <title id="title">{escape(title)}</title>\n'
        f'  <rect width="{width}" height="112" fill="#ffffff"/>\n'
        f'  <image x="16" y="16" width="{width - 32}" height="80" '
        f'preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{payload}"/>\n'
        '</svg>\n'
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for name, title, width in PANELS:
        path = ROOT / "docs/assets/brand" / f"{name}.svg"
        expected = render(name, title, width)
        if args.check:
            if not path.exists() or path.read_text() != expected:
                raise SystemExit(f"Stale README branding: {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected)
    print("PASS: README panels contain unchanged artwork and opaque light backgrounds")


if __name__ == "__main__":
    main()

# Vendored third-party code — NOTICE

This directory contains **unmodified** third-party code vendored into caw-slides to
provide native SVG → PPTX (DrawingML) conversion. It is kept isolated under
`vendor/` and is **not** caw's own code. caw's own slide helpers live in
`skills/caw-slides/scripts/` and `skills/caw-slides/references/`.

## svg_to_pptx, svg_finalize, config.py, console_encoding.py

- **Upstream**: PPT Master — https://github.com/hugohe3/ppt-master
- **Copyright**: © 2025–2026 Hugo He
- **License**: MIT (see `LICENSE` in this directory)
- **Vendored components**:
  - `svg_to_pptx/` — SVG → DrawingML slide/shape conversion package
  - `svg_finalize/` — SVG finalize helpers (tspan flattening etc.) required by the core text/shape path
  - `config.py` — canvas format definitions (`CANVAS_FORMATS`)
  - `console_encoding.py` — UTF-8 stdio helper

MIT permits commercial use and redistribution with attribution; this NOTICE and the
accompanying `LICENSE` satisfy the attribution requirement. The vendored code is
imported as-is; any behavioral changes are made in caw's own wrapper layer, never by
editing these files (so upstream updates can be re-vendored cleanly).

## Runtime dependencies

- **python-pptx** — required (core text/shape/native-chart decks).
- **Pillow** — required only when embedding raster images (e.g. cropped paper figures).
- cairosvg / svglib / reportlab — **not required** by caw's native pipeline (deferred
  imports in the upstream media path that caw does not exercise; avoids a system Cairo
  dependency).

## Re-vendoring / updating

To update, re-copy the four components above from a current PPT Master checkout at the
same relative paths, delete any `__pycache__/`, and re-run the Phase 0 smoke test
(convert a text+shape SVG with only python-pptx installed; assert native AUTO_SHAPE /
TEXT_BOX / FREEFORM shapes, not a single Picture).

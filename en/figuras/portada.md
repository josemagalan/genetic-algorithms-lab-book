# English cover

English adaptation of the approved Spanish cover, prepared with the assistance
of Codex on October 31, 2026. The title is **Evolution Made Visible: Genetic
Algorithms in an Interactive Laboratory**. The five authors, their order, the
palette, and the laboratory motif are preserved.

## Files and regeneration

- `portada.svg`: vertical cover, 1200 × 1800 units (2:3).
- `portada-horizontal.svg`: horizontal adaptation, 1800 × 1000 units.
- `portada.py`: reproducible source using the shared primitives and laboratory
  panel in `../../figuras/portada.py`. Python standard library only.

From the repository root:

```text
python en/figuras/portada.py
```

The SVG files contain editable text, accessible English titles and descriptions,
and no linked assets. They use Arial / Helvetica / sans-serif and Consolas /
monospace, as in the Spanish cover. Fonts are not bundled; rendering depends on
the installed system fonts.

The English build profile uses `figuras/portada.svg` as its cover. The bilingual
generator copies the English SVG files to its isolated English build after
localizing the chapter figures; it leaves the Spanish cover intact.

## Illustration and provenance

The panel retains the geometry of the Spanish illustration. All fourteen labels
are translated; the main title, subtitle, editorial phrases, and footer are
composed in English. No third-party artwork or screenshots are reproduced.

Controls and curves are schematic, not experimental data or a real comparison.
The chromosomes represent parents `10110110` and `01001001`, a cut after the third
bit, and offspring `10101001` and `01010110`; flipping the sixth bit in the second
offspring yields `01010010`. The mutation outline and fragment colors are retained.

The original design and its provenance are documented in `../../figuras/portada.md`.
Illustration: CC BY 4.0 (`LICENSE-CONTENT.md`). Code: MIT (`LICENSE`).

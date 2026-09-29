"""thai_docx — make python-docx output render Thai correctly in Microsoft Word.

Why this exists
---------------
Word does NOT pick a font per run. Inside one run it keeps several "font slots"
and chooses one *per character* based on the character's script:

    - w:ascii / w:hAnsi  -> Latin (Basic Latin, Latin-1)
    - w:cs               -> Complex Script (Thai, Arabic, Hebrew, ...)
    - w:eastAsia         -> CJK

python-docx's ``run.font`` only writes the Latin slot (``w:ascii``/``w:hAnsi``),
the Latin size (``w:sz``), Latin bold (``w:b``) and Latin italic (``w:i``). It
never writes the complex-script twins:

    - w:cs   (complex-script font name)   -> missing => Thai falls back, wrong glyphs
    - w:szCs (complex-script size)        -> missing => Thai shrinks to the default ~10pt
    - w:bCs  (complex-script bold)         -> missing => Thai stays thin under bold
    - w:iCs  (complex-script italic)       -> missing => Thai not italicised
    - w:lang/@w:bidi (complex-script lang) -> missing => bad shaping / mark stacking

LibreOffice and most previewers silently guess the Thai font, so the bug is
invisible there. Real Word on the recipient's machine does not guess, so the
document the client opens is the one that is broken. Trust the verifier
(``verify_thai_docx.py``), never the preview.

``enforce_thai(doc)`` walks every run in the document (body, tables, headers,
footers), every style, and the document defaults, and fills in the missing
complex-script twins so the Latin and Thai slots agree.

Public API
----------
    enforce_thai(doc, ...)        -> mirror Latin props into the CS slots everywhere
    set_run_fonts(run, ...)       -> set Latin + Thai font/size on a single run
    clean_pdf_thai(text)          -> repair Thai text copied out of a PDF
    apply_thai_linebreaks(doc)    -> insert ZWSP at word boundaries (needs pythainlp)
"""

from __future__ import annotations

import re
import unicodedata
import warnings

from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt

# Thai block + Thai-specific combining marks live in U+0E00..U+0E7F.
_THAI_RE = re.compile(r"[฀-๿]")
# Combining vowels/tone marks that must sit on a preceding consonant.
_THAI_COMBINING = (
    "ั"          # mai han-akat
    "ำ"          # sara am (technically spacing, but glued in practice)
    "ิีึืฺุู"  # upper/lower vowels
    "็่้๊๋์ํ๎"  # tone marks + others
)
# Invisible characters that creep in from PDF extraction.
_ZERO_WIDTH = "​‌‍‎‏﻿­⁠"
ZWSP = "​"

DEFAULT_THAI_FONT = "TH Sarabun New"
DEFAULT_THAI_LANG = "th-TH"


def contains_thai(text: str) -> bool:
    """True if the string has at least one Thai character."""
    return bool(text) and bool(_THAI_RE.search(text))


# --------------------------------------------------------------------------- #
# Low-level rPr helpers
# --------------------------------------------------------------------------- #
def _get_or_add(parent, tag: str):
    """Return the child <tag> of parent, creating it (in schema order) if absent."""
    el = parent.find(qn(tag))
    if el is None:
        el = OxmlElement(tag)
        parent.append(el)
    return el


def _fix_rpr(rpr, thai_font, latin_font, thai_lang, force_size):
    """Mirror the Latin run-properties already on ``rpr`` into the CS slots.

    The guiding rule is *do no harm to inherited sizing*. A run that did not
    declare its own ``w:sz`` is inheriting its size from a style (e.g. a
    Heading). If we wrote ``w:szCs`` onto it we would freeze the Thai size and
    break that inheritance — headings would stop scaling. So by default we only
    set ``w:szCs`` when the run already carries an explicit ``w:sz``. Styles and
    docDefaults are fixed separately, which is how no-explicit-size runs still
    get a correct Thai size.
    """
    if rpr is None:
        return

    # --- font names: w:rFonts/@w:cs (+ optionally @w:ascii/@w:hAnsi) ---------
    rfonts = _get_or_add(rpr, "w:rFonts")
    if thai_font:
        rfonts.set(qn("w:cs"), thai_font)
    if latin_font:
        rfonts.set(qn("w:ascii"), latin_font)
        rfonts.set(qn("w:hAnsi"), latin_font)
    elif thai_font and rfonts.get(qn("w:ascii")) is None:
        # No separate Latin font requested and none present: let the Thai font
        # cover Latin too so the run is internally consistent.
        rfonts.set(qn("w:ascii"), thai_font)
        rfonts.set(qn("w:hAnsi"), thai_font)

    # --- size: w:szCs mirrors w:sz -------------------------------------------
    sz = rpr.find(qn("w:sz"))
    if sz is not None and sz.get(qn("w:val")):
        _get_or_add(rpr, "w:szCs").set(qn("w:val"), sz.get(qn("w:val")))
    elif force_size is not None:
        half_points = str(int(round(force_size * 2)))
        _get_or_add(rpr, "w:sz").set(qn("w:val"), half_points)
        _get_or_add(rpr, "w:szCs").set(qn("w:val"), half_points)

    # --- bold / italic: bCs/iCs mirror b/i -----------------------------------
    for latin_tag, cs_tag in (("w:b", "w:bCs"), ("w:i", "w:iCs")):
        latin_el = rpr.find(qn(latin_tag))
        if latin_el is not None:
            cs_el = _get_or_add(rpr, cs_tag)
            val = latin_el.get(qn("w:val"))
            if val is not None:
                cs_el.set(qn("w:val"), val)

    # --- language: w:lang/@w:bidi so Word shapes Thai correctly --------------
    if thai_lang:
        _get_or_add(rpr, "w:lang").set(qn("w:bidi"), thai_lang)


# --------------------------------------------------------------------------- #
# Walking the document
# --------------------------------------------------------------------------- #
def _iter_runs(container):
    """Yield every <w:r> element under a body / header / footer / cell."""
    yield from container.iter(qn("w:r"))


def _fix_runs_in(element, thai_font, latin_font, thai_lang, force_size):
    count = 0
    for r in _iter_runs(element):
        rpr = r.find(qn("w:rPr"))
        if rpr is None:
            rpr = OxmlElement("w:rPr")
            r.insert(0, rpr)
        _fix_rpr(rpr, thai_font, latin_font, thai_lang, force_size)
        count += 1
    return count


def _fix_styles(doc, thai_font, latin_font, thai_lang):
    """Fix the rPr of every style and the document defaults.

    Runs that don't set their own size inherit it here, so this is what keeps
    headings the right size while still getting a Thai font slot. We pass
    force_size=None: never invent a size on a style, only mirror what is there.
    """
    styles_el = doc.styles.element
    for rpr in styles_el.iter(qn("w:rPr")):
        _fix_rpr(rpr, thai_font, latin_font, thai_lang, force_size=None)


def enforce_thai(
    doc,
    thai_font: str = DEFAULT_THAI_FONT,
    latin_font: str | None = None,
    thai_lang: str = DEFAULT_THAI_LANG,
    force_size: float | None = None,
):
    """Make ``doc`` render Thai correctly in Word. Call once, right before save.

    Parameters
    ----------
    thai_font   : font for the complex-script (Thai) slot. Default TH Sarabun New.
    latin_font  : if given, Latin characters use this font while Thai uses
                  ``thai_font`` — in the *same* run, no manual run-splitting.
                  If None, the Thai font also covers Latin.
    thai_lang   : value for w:lang/@w:bidi (default "th-TH").
    force_size  : optional point size to stamp on runs/styles that have no size
                  at all. Usually leave None — explicit sizes are mirrored
                  automatically and inherited sizes are left to inherit.

    Returns the run count touched in the main body (for a quick sanity log).
    """
    body_count = _fix_runs_in(doc.element.body, thai_font, latin_font, thai_lang, force_size)

    for section in doc.sections:
        for hf in (section.header, section.footer,
                   section.first_page_header, section.first_page_footer,
                   section.even_page_header, section.even_page_footer):
            if hf is not None:
                _fix_runs_in(hf._element, thai_font, latin_font, thai_lang, force_size)

    _fix_styles(doc, thai_font, latin_font, thai_lang)
    return body_count


# --------------------------------------------------------------------------- #
# Per-run helper: explicit Latin + Thai fonts/sizes on one run
# --------------------------------------------------------------------------- #
def set_run_fonts(
    run,
    thai_font: str = DEFAULT_THAI_FONT,
    latin_font: str | None = None,
    thai_size_pt: float | None = None,
    latin_size_pt: float | None = None,
    thai_lang: str = DEFAULT_THAI_LANG,
):
    """Set Latin and Thai fonts/sizes on a single run, filling both slots.

    Use this when you build a run by hand and want full control — e.g. Latin in
    Times New Roman 16pt but Thai in TH Sarabun New 18pt within the same run.
    TH Sarabun reads smaller than Latin faces at equal point size, so bumping
    the Thai size a couple points is common.
    """
    rpr = run._element.get_or_add_rPr()
    rfonts = _get_or_add(rpr, "w:rFonts")
    rfonts.set(qn("w:cs"), thai_font)
    latin = latin_font or thai_font
    rfonts.set(qn("w:ascii"), latin)
    rfonts.set(qn("w:hAnsi"), latin)

    if latin_size_pt is not None:
        _get_or_add(rpr, "w:sz").set(qn("w:val"), str(int(round(latin_size_pt * 2))))
    if thai_size_pt is not None:
        _get_or_add(rpr, "w:szCs").set(qn("w:val"), str(int(round(thai_size_pt * 2))))
    elif latin_size_pt is not None:
        _get_or_add(rpr, "w:szCs").set(qn("w:val"), str(int(round(latin_size_pt * 2))))

    if thai_lang:
        _get_or_add(rpr, "w:lang").set(qn("w:bidi"), thai_lang)
    return run


# --------------------------------------------------------------------------- #
# Cleaning Thai pasted from a PDF
# --------------------------------------------------------------------------- #
def clean_pdf_thai(text: str) -> str:
    """Repair Thai text extracted from a PDF.

    PDF text extraction commonly (1) splits combining vowels/tone marks off
    their consonants, (2) injects zero-width and soft-hyphen junk, and (3)
    sprinkles real spaces between Thai characters that should be contiguous.
    This normalises to NFC, strips the invisible junk, and removes spaces that
    sit between two Thai characters or before a Thai combining mark — without
    touching spaces around Latin words or digits.
    """
    if not text:
        return text

    text = unicodedata.normalize("NFC", text)
    text = text.translate({ord(c): None for c in _ZERO_WIDTH})

    # Drop a space sitting between two Thai characters: "ก ข" -> "กข".
    text = re.sub(r"(?<=[฀-๿])[ \t]+(?=[฀-๿])", "", text)
    # Drop any whitespace that ended up before a Thai combining mark.
    text = re.sub(r"\s+(?=[" + _THAI_COMBINING + r"])", "", text)
    # Collapse runs of spaces that are now doubled, but keep newlines.
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


# --------------------------------------------------------------------------- #
# Thai line-break opportunities via zero-width space
# --------------------------------------------------------------------------- #
def apply_thai_linebreaks(doc, engine: str = "newmm") -> int:
    """Insert ZERO WIDTH SPACE at Thai word boundaries in every run.

    Thai has no spaces between words. With justified / thaiDistribute
    alignment some Word builds, lacking a Thai dictionary, break mid-word and
    smear letters across the whole line with huge gaps. Inserting U+200B at real
    word boundaries gives Word legal break points so it breaks between words.

    Needs ``pythainlp`` for tokenisation. If it is not installed this warns and
    returns 0 rather than failing — the document is still valid, just without
    the break hints. Returns the number of runs modified.
    """
    try:
        from pythainlp.tokenize import word_tokenize
    except Exception:
        warnings.warn(
            "pythainlp not installed; skipping Thai line-break hints "
            "(pip install pythainlp). Document saved without ZWSP boundaries."
        )
        return 0

    modified = 0
    for r in _iter_runs(doc.element.body):
        for t in r.findall(qn("w:t")):
            s = t.text
            if not s or not contains_thai(s) or ZWSP in s:
                continue
            tokens = word_tokenize(s, engine=engine, keep_whitespace=True)
            joined = ZWSP.join(tokens)
            # Don't leave a ZWSP hugging an existing space — it's pointless.
            joined = joined.replace(ZWSP + " ", " ").replace(" " + ZWSP, " ")
            if joined != s:
                t.text = joined
                modified += 1
    return modified


__all__ = [
    "enforce_thai",
    "set_run_fonts",
    "clean_pdf_thai",
    "apply_thai_linebreaks",
    "contains_thai",
    "DEFAULT_THAI_FONT",
    "DEFAULT_THAI_LANG",
    "ZWSP",
]

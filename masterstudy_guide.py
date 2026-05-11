from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ── Color Palette ──────────────────────────────────────────────────────────────
DARK_BG       = colors.HexColor("#0F172A")   # slate-900
CARD_BG       = colors.HexColor("#1E293B")   # slate-800
ACCENT_BLUE   = colors.HexColor("#3B82F6")   # blue-500
ACCENT_GREEN  = colors.HexColor("#10B981")   # emerald-500
ACCENT_PURPLE = colors.HexColor("#8B5CF6")   # violet-500
ACCENT_ORANGE = colors.HexColor("#F59E0B")   # amber-500
ACCENT_RED    = colors.HexColor("#EF4444")   # red-500
ACCENT_CYAN   = colors.HexColor("#06B6D4")   # cyan-500
TEXT_WHITE    = colors.HexColor("#F8FAFC")   # slate-50
TEXT_GRAY     = colors.HexColor("#94A3B8")   # slate-400
TEXT_DARK     = colors.HexColor("#1E293B")   # slate-800
CODE_BG       = colors.HexColor("#0D1117")   # github dark
CODE_TEXT     = colors.HexColor("#E6EDF3")
HIGHLIGHT_YEL = colors.HexColor("#FEF3C7")
BORDER_COLOR  = colors.HexColor("#334155")

W, H = A4

# ── Track color map ────────────────────────────────────────────────────────────
TRACK_COLORS = {
    "dsa":     ACCENT_GREEN,
    "ml":      ACCENT_PURPLE,
    "python":  ACCENT_BLUE,
    "sysdes":  ACCENT_ORANGE,
    "rest":    ACCENT_CYAN,
}

# ── Style helpers ──────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

STYLE_COVER_TITLE = S("CoverTitle",
    fontSize=34, leading=42, textColor=TEXT_WHITE,
    fontName="Helvetica-Bold", alignment=TA_CENTER)

STYLE_COVER_SUB = S("CoverSub",
    fontSize=14, leading=20, textColor=TEXT_GRAY,
    fontName="Helvetica", alignment=TA_CENTER)

STYLE_TRACK_BADGE = S("TrackBadge",
    fontSize=10, textColor=TEXT_WHITE,
    fontName="Helvetica-Bold", alignment=TA_CENTER)

STYLE_CHAPTER = S("Chapter",
    fontSize=26, leading=34, textColor=TEXT_WHITE,
    fontName="Helvetica-Bold", alignment=TA_LEFT, spaceAfter=6)

STYLE_SECTION = S("Section",
    fontSize=16, leading=22, textColor=ACCENT_BLUE,
    fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=14)

STYLE_SUBSECTION = S("Subsection",
    fontSize=13, leading=18, textColor=TEXT_WHITE,
    fontName="Helvetica-Bold", spaceAfter=3, spaceBefore=8)

STYLE_BODY = S("Body",
    fontSize=10.5, leading=16, textColor=TEXT_WHITE,
    fontName="Helvetica", spaceAfter=6, alignment=TA_JUSTIFY)

STYLE_BODY_DARK = S("BodyDark",
    fontSize=10.5, leading=16, textColor=TEXT_DARK,
    fontName="Helvetica", spaceAfter=6, alignment=TA_JUSTIFY)

STYLE_CODE = S("Code",
    fontSize=9, leading=14, textColor=CODE_TEXT,
    fontName="Courier", spaceAfter=2)

STYLE_BULLET = S("Bullet",
    fontSize=10.5, leading=16, textColor=TEXT_WHITE,
    fontName="Helvetica", leftIndent=14, spaceAfter=3,
    bulletIndent=0)

STYLE_INSIGHT = S("Insight",
    fontSize=10.5, leading=16, textColor=TEXT_DARK,
    fontName="Helvetica-Bold", spaceAfter=4)

STYLE_LABEL = S("Label",
    fontSize=9, leading=12, textColor=ACCENT_GREEN,
    fontName="Helvetica-Bold")

STYLE_TOC_ITEM = S("TOCItem",
    fontSize=11, leading=18, textColor=TEXT_WHITE,
    fontName="Helvetica")

STYLE_TOC_TRACK = S("TOCTrack",
    fontSize=13, leading=20, textColor=ACCENT_BLUE,
    fontName="Helvetica-Bold")

# ── Custom Flowables ───────────────────────────────────────────────────────────

class ColorRect(Flowable):
    """A solid-colored rectangle as a background block."""
    def __init__(self, width, height, color, radius=4):
        super().__init__()
        self.width = width
        self.height = height
        self.color = color
        self.radius = radius

    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.roundRect(0, 0, self.width, self.height, self.radius, fill=1, stroke=0)


class CodeBlock(Flowable):
    """Renders a code block with dark background."""
    def __init__(self, code, width=None, lang="python", accent=ACCENT_GREEN):
        super().__init__()
        self._code = code
        self._width = width or (W - 60*mm)
        self._lang = lang
        self._accent = accent
        self._lines = code.strip().split("\n")
        self._line_h = 13
        self._pad = 10
        self.height = len(self._lines) * self._line_h + self._pad * 2 + 18

    def wrap(self, aw, ah):
        self._width = min(self._width, aw)
        return self._width, self.height

    def draw(self):
        c = self.canv
        w, h = self._width, self.height
        # Background
        c.setFillColor(CODE_BG)
        c.roundRect(0, 0, w, h, 5, fill=1, stroke=0)
        # Top bar
        c.setFillColor(self._accent)
        c.roundRect(0, h - 18, w, 18, 5, fill=1, stroke=0)
        c.setFillColor(CODE_BG)
        c.rect(0, h - 18, w, 9, fill=1, stroke=0)
        # Language label
        c.setFillColor(TEXT_WHITE)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(8, h - 13, self._lang.upper())
        # Dots
        for i, col in enumerate([colors.HexColor("#FF5F57"),
                                   colors.HexColor("#FEBC2E"),
                                   colors.HexColor("#28C840")]):
            c.setFillColor(col)
            c.circle(w - 14 - i * 14, h - 9, 4, fill=1, stroke=0)
        # Code lines
        c.setFillColor(CODE_TEXT)
        c.setFont("Courier", 9)
        for i, line in enumerate(self._lines):
            y = h - 18 - self._pad - (i + 1) * self._line_h + 3
            # Syntax-like coloring (basic)
            c.drawString(self._pad, y, line)


class SectionHeader(Flowable):
    """Colored section header band."""
    def __init__(self, text, color=ACCENT_BLUE, width=None):
        super().__init__()
        self._text = text
        self._color = color
        self._width = width or (W - 40*mm)
        self.height = 28

    def wrap(self, aw, ah):
        self._width = aw
        return aw, self.height

    def draw(self):
        c = self.canv
        w, h = self._width, self.height
        c.setFillColor(self._color)
        c.roundRect(0, 0, w, h, 4, fill=1, stroke=0)
        c.setFillColor(TEXT_WHITE)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(10, 8, self._text)


class InsightBox(Flowable):
    """A highlighted insight/tip box."""
    def __init__(self, title, text, color=ACCENT_ORANGE, width=None):
        super().__init__()
        self._title = title
        self._text = text
        self._color = color
        self._width = width or (W - 40*mm)
        # Estimate height
        chars_per_line = int(self._width / 6)
        lines = max(3, len(text) // chars_per_line + 2)
        self.height = lines * 14 + 30

    def wrap(self, aw, ah):
        self._width = aw
        return aw, self.height

    def draw(self):
        c = self.canv
        w, h = self._width, self.height
        # Border + light bg
        c.setFillColor(colors.HexColor("#FFF7ED"))
        c.setStrokeColor(self._color)
        c.setLineWidth(2)
        c.roundRect(0, 0, w, h, 5, fill=1, stroke=1)
        # Left accent bar
        c.setFillColor(self._color)
        c.rect(0, 0, 5, h, fill=1, stroke=0)
        # Title
        c.setFillColor(self._color)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(14, h - 16, f"💡  {self._title}")
        # Body text
        c.setFillColor(TEXT_DARK)
        c.setFont("Helvetica", 9.5)
        # Simple word wrap
        words = self._text.split()
        line, lines_out = "", []
        for w_word in words:
            test = (line + " " + w_word).strip()
            if len(test) * 5.8 > w - 24:
                lines_out.append(line)
                line = w_word
            else:
                line = test
        lines_out.append(line)
        for i, ln in enumerate(lines_out):
            c.drawString(14, h - 32 - i * 14, ln)


class ChapterBanner(Flowable):
    """Full-width chapter header banner."""
    def __init__(self, track_label, title, subtitle, color, width=None):
        super().__init__()
        self._track = track_label
        self._title = title
        self._subtitle = subtitle
        self._color = color
        self._width = width or (W - 40*mm)
        self.height = 90

    def wrap(self, aw, ah):
        self._width = aw
        return aw, self.height

    def draw(self):
        c = self.canv
        w, h = self._width, self.height
        # BG
        c.setFillColor(CARD_BG)
        c.roundRect(0, 0, w, h, 6, fill=1, stroke=0)
        # Left accent
        c.setFillColor(self._color)
        c.rect(0, 0, 7, h, fill=1, stroke=0)
        # Track badge
        c.setFillColor(self._color)
        c.roundRect(16, h - 26, len(self._track) * 7.5 + 14, 18, 4, fill=1, stroke=0)
        c.setFillColor(TEXT_WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(23, h - 20, self._track)
        # Title
        c.setFillColor(TEXT_WHITE)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(16, h - 52, self._title)
        # Subtitle
        c.setFillColor(TEXT_GRAY)
        c.setFont("Helvetica", 10)
        c.drawString(16, h - 68, self._subtitle)
        # Bottom line
        c.setStrokeColor(self._color)
        c.setLineWidth(1)
        c.line(16, 10, w - 10, 10)


class DifficultyBadge(Flowable):
    """Difficulty badge for LeetCode problems."""
    def __init__(self, problem, difficulty, lc_num, color=None):
        super().__init__()
        self._problem = problem
        self._diff = difficulty
        self._num = lc_num
        self._color = color or (ACCENT_GREEN if difficulty == "Easy"
                                else ACCENT_ORANGE if difficulty == "Medium"
                                else ACCENT_RED)
        self.height = 24

    def wrap(self, aw, ah):
        return aw, self.height

    def draw(self):
        c = self.canv
        # LC number
        c.setFillColor(ACCENT_BLUE)
        c.roundRect(0, 2, 48, 18, 3, fill=1, stroke=0)
        c.setFillColor(TEXT_WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(5, 7, f"LC #{self._num}")
        # Problem name
        c.setFillColor(TEXT_WHITE)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(56, 7, self._problem)
        # Difficulty
        c.setFillColor(self._color)
        label_w = len(self._diff) * 7 + 12
        c.roundRect(56 + len(self._problem) * 7 + 8, 2, label_w, 18, 3, fill=1, stroke=0)
        c.setFillColor(TEXT_WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(56 + len(self._problem) * 7 + 14, 7, self._diff)


# ── Page template callbacks ────────────────────────────────────────────────────

def on_page(canvas, doc):
    canvas.saveState()
    # Dark full-page background
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # Footer
    canvas.setFillColor(BORDER_COLOR)
    canvas.rect(20*mm, 10*mm, W - 40*mm, 0.5, fill=1, stroke=0)
    canvas.setFillColor(TEXT_GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(20*mm, 7*mm, "Day 1–2 Master Study Guide  |  Beginner → Advanced")
    canvas.drawRightString(W - 20*mm, 7*mm, f"Page {doc.page}")
    canvas.restoreState()


def on_first_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.restoreState()


# ── Content builder ────────────────────────────────────────────────────────────

def build_doc():
    path = "/mnt/user-data/outputs/Day1_2_MasterStudyGuide.pdf"
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm, bottomMargin=18*mm,
    )

    story = []
    add = story.append

    # ─────────────────────── COVER ───────────────────────────────────────────
    add(Spacer(1, 40*mm))
    # Accent bar
    add(ColorRect(W - 40*mm, 4, ACCENT_BLUE))
    add(Spacer(1, 8*mm))
    add(Paragraph("DAY 1–2 MASTER", STYLE_COVER_TITLE))
    add(Paragraph("STUDY GUIDE", S("CT2", fontSize=42, leading=50, textColor=ACCENT_BLUE,
                                    fontName="Helvetica-Bold", alignment=TA_CENTER)))
    add(Spacer(1, 6*mm))
    add(ColorRect(W - 40*mm, 4, ACCENT_BLUE))
    add(Spacer(1, 10*mm))
    add(Paragraph("Beginner → Advanced  ·  Deep Dives  ·  Code Examples  ·  Interview Patterns",
                   STYLE_COVER_SUB))
    add(Spacer(1, 14*mm))

    # Track pills
    tracks = [
        ("🔢  Arrays & Hashing", ACCENT_GREEN),
        ("👆  Two Pointers", ACCENT_CYAN),
        ("🤖  Transformers", ACCENT_PURPLE),
        ("🐍  CPython Internals", ACCENT_BLUE),
        ("☁️  CAP Theorem", ACCENT_ORANGE),
        ("🌐  REST API Design", ACCENT_RED),
    ]
    track_data = [[Paragraph(f'<font color="white"><b>{t}</b></font>',
                              S("tp", fontSize=10, fontName="Helvetica-Bold",
                                alignment=TA_CENTER, textColor=TEXT_WHITE))
                   for t, _ in tracks[:3]],
                  [Paragraph(f'<font color="white"><b>{t}</b></font>',
                              S("tp", fontSize=10, fontName="Helvetica-Bold",
                                alignment=TA_CENTER, textColor=TEXT_WHITE))
                   for t, _ in tracks[3:]]]

    t = Table([track_data[0]], colWidths=[(W-40*mm)/3]*3, rowHeights=[28])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), ACCENT_GREEN),
        ("BACKGROUND", (1,0), (1,0), ACCENT_CYAN),
        ("BACKGROUND", (2,0), (2,0), ACCENT_PURPLE),
        ("ROUNDEDCORNERS", [4]),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
    ]))
    add(t)
    add(Spacer(1, 4))
    t2 = Table([track_data[1]], colWidths=[(W-40*mm)/3]*3, rowHeights=[28])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), ACCENT_BLUE),
        ("BACKGROUND", (1,0), (1,0), ACCENT_ORANGE),
        ("BACKGROUND", (2,0), (2,0), ACCENT_RED),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    add(t2)
    add(Spacer(1, 20*mm))
    add(Paragraph("6 Topics  ·  30+ Code Examples  ·  LeetCode Solutions  ·  System Design Patterns",
                   STYLE_COVER_SUB))
    add(PageBreak())

    # ─────────────────────── TABLE OF CONTENTS ───────────────────────────────
    add(Spacer(1, 8*mm))
    add(SectionHeader("  TABLE OF CONTENTS", ACCENT_BLUE))
    add(Spacer(1, 6*mm))

    toc_items = [
        ("DSA — Arrays & Hashing", [
            "1.1  What Is a HashMap? O(1) Magic Explained",
            "1.2  Frequency Maps & Counting Patterns",
            "1.3  Prefix Sums & Difference Arrays",
            "1.4  LeetCode Problems: Two Sum, Contains Duplicate, Valid Anagram, Group Anagrams, Top K Frequent",
        ], ACCENT_GREEN),
        ("DSA — Two Pointers", [
            "2.1  Left/Right Pointers on Sorted Arrays",
            "2.2  Fast/Slow Pointer Pattern (Floyd's Algorithm)",
            "2.3  LeetCode Problems: Valid Palindrome, 3Sum, Container With Most Water, Trapping Rain Water, Move Zeroes",
        ], ACCENT_CYAN),
        ("ML — Transformer Architecture", [
            "3.1  The Original Transformer (Vaswani et al. 2017)",
            "3.2  Attention Mechanism Deep Dive (Q, K, V)",
            "3.3  Multi-Head Attention, Positional Encodings, Layer Norm",
            "3.4  Modern Variants: GQA, RoPE, SwiGLU, FlashAttention",
        ], ACCENT_PURPLE),
        ("Python — CPython Internals", [
            "4.1  PyObject Structure & Reference Counting",
            "4.2  Memory Allocator: pymalloc vs system malloc",
            "4.3  Integer Cache, String Interning, id() vs is",
            "4.4  Bytecode & the dis Module",
        ], ACCENT_BLUE),
        ("System Design — CAP Theorem", [
            "5.1  CAP Theorem Explained with Real Systems",
            "5.2  Consistency Spectrum: Strong → Eventual",
            "5.3  PACELC Extension, Read-Your-Writes, Monotonic Reads",
        ], ACCENT_ORANGE),
        ("System Design — REST API Design", [
            "6.1  REST Constraints & HTTP Method Semantics",
            "6.2  Status Codes Reference",
            "6.3  API Versioning, Pagination Strategies",
            "6.4  HATEOAS & Richardson Maturity Model",
        ], ACCENT_RED),
    ]

    for track_title, items, color in toc_items:
        col_hex = color.hexval().replace("0x", "#").upper()
        add(Paragraph(f'<font color="{col_hex}">'
                       f'▶  {track_title}</font>',
                       STYLE_TOC_TRACK))
        for item in items:
            add(Paragraph(f"    {item}", STYLE_TOC_ITEM))
        add(Spacer(1, 4*mm))

    add(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 1: ARRAYS & HASHING
    # ═══════════════════════════════════════════════════════════════════════════
    add(ChapterBanner("DSA  ·  DAY 1", "Arrays & Hashing",
                       "HashMap fundamentals · Frequency maps · Prefix sums · 5 LeetCode problems",
                       ACCENT_GREEN))
    add(Spacer(1, 6*mm))

    add(SectionHeader("  1.1  What Is a HashMap? (The O(1) Magic)", ACCENT_GREEN))
    add(Spacer(1, 3*mm))

    add(Paragraph(
        "A <b>HashMap</b> (called <b>dict</b> in Python) is a data structure that stores key-value pairs "
        "and provides <b>average O(1) time complexity</b> for lookup, insert, and delete operations. "
        "Understanding WHY it's O(1) is critical — it's all about hashing.",
        STYLE_BODY))

    add(Paragraph("How Hashing Works — Step by Step:", STYLE_SUBSECTION))
    add(Paragraph(
        "1. You call <b>hash(key)</b> — Python converts your key into a large integer (the hash value).<br/>"
        "2. This integer is mapped to a <b>bucket index</b> using <b>index = hash(key) % table_size</b>.<br/>"
        "3. The value is stored at that bucket. Lookup = same 2 steps → <b>O(1)</b>.<br/>"
        "4. <b>Collision</b>: Two keys map to the same bucket. Python resolves via <b>open addressing</b> "
        "(probing nearby slots).",
        STYLE_BODY))

    add(CodeBlock("""# Basic HashMap operations — all O(1) average
d = {}

# Insert / Update — O(1)
d["apple"] = 5
d["banana"] = 3
d["apple"] = 10   # updates in-place

# Lookup — O(1)
val = d.get("apple", 0)   # returns 10 (default 0 if missing)
exists = "banana" in d    # True — O(1) membership check

# Delete — O(1)
del d["banana"]

# Safe access patterns
count = d.get("cherry", 0)   # won't throw KeyError
d.setdefault("grape", []).append(1)   # init if missing

print(d)  # {'apple': 10, 'grape': [1]}""", lang="Python", accent=ACCENT_GREEN))

    add(Spacer(1, 3*mm))
    add(Paragraph("Python Dict Internals (What Interviews Expect You to Know):", STYLE_SUBSECTION))
    add(Paragraph(
        "Python dicts use a <b>hash table with open addressing</b>. Since Python 3.7+, dicts are also "
        "<b>ordered by insertion order</b> (guaranteed by the language spec). The load factor is kept "
        "below ~2/3 — when the table fills up, Python resizes it (doubles the table), which is an O(N) "
        "operation. This is amortized, so average insert is still O(1).",
        STYLE_BODY))

    add(InsightBox("Interview Insight",
        "HashMap problems are 30%+ of FAANG Easy rounds. The pattern is almost always: "
        "'How do I avoid the O(N²) brute force?' Answer: store something in a dict on the first pass, "
        "look it up on the second pass.", ACCENT_GREEN))
    add(Spacer(1, 4*mm))

    # ── 1.2 Frequency Maps
    add(SectionHeader("  1.2  Frequency Maps & Counting Patterns", ACCENT_GREEN))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "A <b>Frequency Map</b> counts how many times each element appears. It's the foundation "
        "of anagram detection, top-K queries, and majority element problems. Three idiomatic ways in Python:",
        STYLE_BODY))

    add(CodeBlock("""from collections import Counter, defaultdict

nums = [1, 3, 2, 3, 1, 3, 4]

# Method 1: Manual dict
freq = {}
for n in nums:
    freq[n] = freq.get(n, 0) + 1
# {1:2, 3:3, 2:1, 4:1}

# Method 2: defaultdict (cleanest for beginners)
freq2 = defaultdict(int)
for n in nums:
    freq2[n] += 1

# Method 3: Counter (most Pythonic)
freq3 = Counter(nums)
print(freq3.most_common(2))   # [(3, 3), (1, 2)] — top 2

# Grouping by key (anagram grouping pattern)
words = ["eat", "tea", "tan", "ate", "nat", "bat"]
groups = defaultdict(list)
for word in words:
    key = tuple(sorted(word))   # canonical form
    groups[key].append(word)

print(list(groups.values()))
# [['eat','tea','ate'], ['tan','nat'], ['bat']]""", lang="Python", accent=ACCENT_GREEN))

    add(Spacer(1, 3*mm))

    # ── 1.3 Prefix Sums
    add(SectionHeader("  1.3  Prefix Sums & Difference Arrays", ACCENT_GREEN))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "<b>Prefix Sum</b>: precompute cumulative sums so any subarray sum query becomes O(1). "
        "Instead of summing from i to j each time (O(N) per query), precompute prefix[i] = sum(arr[0..i-1]). "
        "Then sum(i, j) = prefix[j+1] - prefix[i].",
        STYLE_BODY))

    add(CodeBlock("""# Prefix Sum — turn O(N) range queries into O(1)
arr = [2, 4, 1, 7, 3, 5]

# Build prefix sum array
prefix = [0] * (len(arr) + 1)
for i, val in enumerate(arr):
    prefix[i+1] = prefix[i] + val
# prefix = [0, 2, 6, 7, 14, 17, 22]

def range_sum(l, r):   # inclusive [l, r]
    return prefix[r+1] - prefix[l]

print(range_sum(1, 4))   # 4+1+7+3 = 15 ← O(1)!
print(range_sum(0, 5))   # 2+4+1+7+3+5 = 22

# ── Difference Array ── for range update queries ──
# Problem: add val to arr[l..r] for Q queries, then output final array.
# Naive: O(N) per update = O(NQ). Difference array: O(1) per update!

def apply_range_updates(n, updates):
    diff = [0] * (n + 1)
    for l, r, val in updates:
        diff[l] += val
        diff[r+1] -= val   # sentinel stop
    # Prefix sum of diff = final array
    result, running = [], 0
    for i in range(n):
        running += diff[i]
        result.append(running)
    return result

arr = apply_range_updates(6, [(1,3,10), (2,5,5), (0,2,-3)])
print(arr)   # [-3, 7, 12, 15, 5, 5]""", lang="Python", accent=ACCENT_GREEN))

    add(Spacer(1, 4*mm))

    # ── LeetCode Problems
    add(SectionHeader("  1.4  LeetCode Solutions — Arrays & Hashing", ACCENT_GREEN))
    add(Spacer(1, 3*mm))

    # Two Sum
    add(DifficultyBadge("Two Sum", "Easy", "1"))
    add(Spacer(1, 2*mm))
    add(Paragraph(
        "<b>Problem:</b> Given array nums and a target, return indices of two numbers that add to target.<br/>"
        "<b>Key Insight:</b> For each number x, we need (target - x). Store seen numbers in a dict. "
        "One pass: check if complement exists BEFORE adding current to dict.",
        STYLE_BODY))
    add(CodeBlock("""def twoSum(nums, target):
    seen = {}   # value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:           # O(1) lookup!
            return [seen[complement], i]
        seen[num] = i
    return []   # no solution (problem guarantees one exists)

# Trace: nums=[2,7,11,15], target=9
# i=0: num=2, need 7, not seen → seen={2:0}
# i=1: num=7, need 2, found at idx 0 → return [0,1]

# Time: O(N) | Space: O(N)
# vs Brute Force: O(N²) time, O(1) space
print(twoSum([2,7,11,15], 9))    # [0,1]
print(twoSum([3,2,4], 6))        # [1,2]
print(twoSum([3,3], 6))          # [0,1]""", lang="Python", accent=ACCENT_GREEN))
    add(Spacer(1, 3*mm))

    # Contains Duplicate
    add(DifficultyBadge("Contains Duplicate", "Easy", "217"))
    add(Spacer(1, 2*mm))
    add(Paragraph(
        "<b>Problem:</b> Return True if any value appears at least twice.<br/>"
        "<b>Key Insight:</b> Use a set for O(1) membership checks. Sets are hash tables under the hood.",
        STYLE_BODY))
    add(CodeBlock("""def containsDuplicate(nums):
    seen = set()
    for num in nums:
        if num in seen:     # O(1) check
            return True
        seen.add(num)
    return False

# One-liner (Pythonic):
def containsDuplicate_v2(nums):
    return len(set(nums)) != len(nums)
# Careful: v2 always builds full set (no early exit)
# v1 short-circuits on first duplicate → faster in practice

print(containsDuplicate([1,2,3,1]))   # True
print(containsDuplicate([1,2,3,4]))   # False""", lang="Python", accent=ACCENT_GREEN))
    add(Spacer(1, 3*mm))

    # Valid Anagram
    add(DifficultyBadge("Valid Anagram", "Easy", "242"))
    add(Spacer(1, 2*mm))
    add(Paragraph(
        "<b>Problem:</b> Return True if t is an anagram of s (same chars, same counts).<br/>"
        "<b>Three approaches — know all three for interviews:</b>",
        STYLE_BODY))
    add(CodeBlock("""from collections import Counter

def isAnagram(s, t):
    # Approach 1: Sort (O(N log N)) — easiest to write
    return sorted(s) == sorted(t)

def isAnagram_v2(s, t):
    # Approach 2: Counter (O(N)) — most Pythonic
    return Counter(s) == Counter(t)

def isAnagram_v3(s, t):
    # Approach 3: Manual (O(N)) — shows you understand internals
    if len(s) != len(t): return False
    count = {}
    for c in s: count[c] = count.get(c, 0) + 1
    for c in t:
        if c not in count or count[c] == 0:
            return False
        count[c] -= 1
    return True

# Follow-up: What if chars are Unicode? → use dict, not fixed array
# Follow-up: Stream of strings? → maintain running counter

print(isAnagram_v2("anagram", "nagaram"))  # True
print(isAnagram_v2("rat", "car"))          # False""", lang="Python", accent=ACCENT_GREEN))
    add(Spacer(1, 3*mm))

    # Group Anagrams
    add(DifficultyBadge("Group Anagrams", "Medium", "49"))
    add(Spacer(1, 2*mm))
    add(Paragraph(
        "<b>Problem:</b> Group all anagrams together from a list of strings.<br/>"
        "<b>Key Insight:</b> Anagrams share the same sorted string — use sorted string as the dict key. "
        "Alternative: use character count tuple as key (avoids sort cost).",
        STYLE_BODY))
    add(CodeBlock("""from collections import defaultdict

def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))      # 'eat' → ('a','e','t')
        groups[key].append(s)
    return list(groups.values())

# Optimized: O(N*K) instead of O(N*K log K) where K = max string length
def groupAnagrams_v2(strs):
    groups = defaultdict(list)
    for s in strs:
        count = [0] * 26            # a-z frequency
        for c in s:
            count[ord(c) - ord('a')] += 1
        groups[tuple(count)].append(s)   # tuple is hashable
    return list(groups.values())

strs = ["eat","tea","tan","ate","nat","bat"]
print(groupAnagrams(strs))
# [['eat','tea','ate'], ['tan','nat'], ['bat']]
# Time: O(N*K log K) | Space: O(N*K)""", lang="Python", accent=ACCENT_GREEN))
    add(Spacer(1, 3*mm))

    # Top K Frequent
    add(DifficultyBadge("Top K Frequent Elements", "Medium", "347"))
    add(Spacer(1, 2*mm))
    add(Paragraph(
        "<b>Problem:</b> Return the k most frequent elements.<br/>"
        "<b>Three approaches — Bucket Sort is the O(N) gem!</b>",
        STYLE_BODY))
    add(CodeBlock("""import heapq
from collections import Counter

def topKFrequent_heap(nums, k):
    # Approach 1: Heap — O(N log K)
    count = Counter(nums)
    return heapq.nlargest(k, count.keys(), key=count.get)

def topKFrequent_sort(nums, k):
    # Approach 2: Sort — O(N log N) — simplest but slower
    count = Counter(nums)
    return sorted(count, key=count.get, reverse=True)[:k]

def topKFrequent_bucket(nums, k):
    # Approach 3: Bucket Sort — O(N) OPTIMAL
    # Key insight: frequency can be at most len(nums)
    count = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]
    for num, freq in count.items():
        buckets[freq].append(num)   # index = frequency
    # Read from highest frequency bucket down
    result = []
    for freq in range(len(buckets) - 1, 0, -1):
        result.extend(buckets[freq])
        if len(result) >= k:
            return result[:k]
    return result

nums = [1,1,1,2,2,3]
print(topKFrequent_bucket(nums, 2))   # [1, 2]
# Time: O(N) | Space: O(N)""", lang="Python", accent=ACCENT_GREEN))

    add(Spacer(1, 4*mm))
    add(InsightBox("Chapter Summary",
        "Arrays & Hashing: The core insight is trading space for time. A HashMap turns O(N) search "
        "into O(1) lookup. Frequency maps let you count, group, and rank elements efficiently. "
        "Prefix sums turn O(N) range queries into O(1). These 3 tools solve 30%+ of Easy interview problems.",
        ACCENT_GREEN))
    add(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 2: TWO POINTERS
    # ═══════════════════════════════════════════════════════════════════════════
    add(ChapterBanner("DSA  ·  DAY 2", "Two Pointers",
                       "Left/right pointers · Fast/slow pointers · O(N) from O(N²) · 5 LeetCode problems",
                       ACCENT_CYAN))
    add(Spacer(1, 6*mm))

    add(SectionHeader("  2.1  The Core Idea — Why Two Pointers?", ACCENT_CYAN))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "The <b>Two Pointer technique</b> eliminates one loop by maintaining two indices that move "
        "toward each other (or in the same direction). It converts many O(N²) brute-force solutions "
        "into O(N). The key prerequisite: <b>the array must be sorted</b> (or be a palindrome check, "
        "or the structure must allow us to reason about pointer movement).",
        STYLE_BODY))

    add(Paragraph("Pattern Recognition Checklist:", STYLE_SUBSECTION))
    checks = [
        "Find a pair with a target sum in a sorted array → Two Pointers (left + right)",
        "Remove duplicates in-place from sorted array → Two Pointers (read + write pointer)",
        "Check if string is a palindrome → Two Pointers (start + end)",
        "Merge two sorted arrays → Two Pointers (one per array)",
        "Detect a cycle in a linked list → Fast/Slow pointers (Floyd's algorithm)",
        "Find container with most water / trapping rain water → Two Pointers",
    ]
    for c in checks:
        add(Paragraph(f"✓  {c}", STYLE_BULLET))
    add(Spacer(1, 3*mm))

    add(CodeBlock("""# Template: Left/Right two pointers on sorted array
def two_pointer_template(arr, target):
    arr.sort()               # if not already sorted
    left, right = 0, len(arr) - 1

    while left < right:      # CRITICAL: strict < not <=
        current = arr[left] + arr[right]
        if current == target:
            return [left, right]          # found!
        elif current < target:
            left += 1        # need larger sum → move left pointer right
        else:
            right -= 1       # need smaller sum → move right pointer left
    return []

# WHY does this work?
# In a sorted array, moving left pointer RIGHT increases the sum.
# Moving right pointer LEFT decreases the sum.
# So we can navigate the 2D search space in 1D → O(N) instead of O(N²)""",
                   lang="Python", accent=ACCENT_CYAN))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  2.2  Fast/Slow Pointers (Floyd's Cycle Detection)", ACCENT_CYAN))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "The <b>Fast/Slow pointer</b> (Tortoise and Hare) technique uses two pointers moving at different "
        "speeds. If a cycle exists, the fast pointer eventually laps the slow pointer. Used for: "
        "detecting cycles in linked lists, finding the middle of a list, finding the start of a cycle.",
        STYLE_BODY))

    add(CodeBlock("""# Example 1: Detect cycle in linked list — O(N) time, O(1) space
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def hasCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next          # move 1 step
        fast = fast.next.next    # move 2 steps
        if slow is fast:          # they met! cycle exists
            return True
    return False                  # fast reached end → no cycle

# Example 2: Find MIDDLE of linked list — O(N), O(1)
def findMiddle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow   # when fast reaches end, slow is at middle

# Example 3: Find start of cycle (LeetCode 142)
def detectCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            # Reset slow to head, keep fast at meeting point
            slow = head
            while slow is not fast:
                slow = slow.next
                fast = fast.next
            return slow   # start of cycle!
    return None""", lang="Python", accent=ACCENT_CYAN))
    add(Spacer(1, 4*mm))

    add(SectionHeader("  2.3  LeetCode Solutions — Two Pointers", ACCENT_CYAN))
    add(Spacer(1, 3*mm))

    # Valid Palindrome
    add(DifficultyBadge("Valid Palindrome", "Easy", "125"))
    add(Spacer(1, 2*mm))
    add(Paragraph(
        "<b>Problem:</b> A phrase is a palindrome if, after converting to lowercase and removing "
        "non-alphanumeric chars, it reads the same forward and backward.",
        STYLE_BODY))
    add(CodeBlock("""def isPalindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        # Skip non-alphanumeric from both sides
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True

# Trace: s = "A man, a plan, a canal: Panama"
# left=0 'A', right=29 'a' → match
# left=2 'm', right=27 'm' → match ... → True

print(isPalindrome("A man, a plan, a canal: Panama"))  # True
print(isPalindrome("race a car"))                       # False
# Time: O(N) | Space: O(1) — no extra string created!""", lang="Python", accent=ACCENT_CYAN))
    add(Spacer(1, 3*mm))

    # 3Sum
    add(DifficultyBadge("3Sum", "Medium", "15"))
    add(Spacer(1, 2*mm))
    add(Paragraph(
        "<b>Problem:</b> Find all unique triplets that sum to 0.<br/>"
        "<b>Key Insight:</b> Sort, fix one element with outer loop, then Two Pointers for remaining two. "
        "Skip duplicates carefully!",
        STYLE_BODY))
    add(CodeBlock("""def threeSum(nums):
    nums.sort()               # MUST sort first
    result = []

    for i in range(len(nums) - 2):
        # Skip duplicate values for the fixed element
        if i > 0 and nums[i] == nums[i-1]:
            continue

        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                # Skip duplicates for left and right too!
                while left < right and nums[left] == nums[left+1]:
                    left += 1
                while left < right and nums[right] == nums[right-1]:
                    right -= 1
                left += 1
                right -= 1
            elif total < 0:
                left += 1    # need larger sum
            else:
                right -= 1   # need smaller sum
    return result

print(threeSum([-1,0,1,2,-1,-4]))   # [[-1,-1,2],[-1,0,1]]
print(threeSum([0,0,0]))            # [[0,0,0]]
# Time: O(N²) | Space: O(1) excluding output""", lang="Python", accent=ACCENT_CYAN))
    add(Spacer(1, 3*mm))

    # Container With Most Water
    add(DifficultyBadge("Container With Most Water", "Medium", "11"))
    add(Spacer(1, 2*mm))
    add(Paragraph(
        "<b>Problem:</b> Given heights, find two lines that together with the x-axis form a container "
        "that holds the most water.<br/>"
        "<b>Greedy Insight:</b> Water = min(height[l], height[r]) × (r - l). "
        "Always move the pointer with the SMALLER height — moving the taller one can only decrease area.",
        STYLE_BODY))
    add(CodeBlock("""def maxArea(height):
    left, right = 0, len(height) - 1
    max_water = 0

    while left < right:
        width = right - left
        h = min(height[left], height[right])
        max_water = max(max_water, width * h)

        # Move the shorter side — WHY?
        # Current area is limited by the shorter side.
        # Moving the TALLER side can only reduce width while
        # the height is still bounded by the shorter side → no gain.
        # Moving SHORTER side might find a taller line → possible gain.
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return max_water

print(maxArea([1,8,6,2,5,4,8,3,7]))   # 49
# Heights 8 (idx 1) and 7 (idx 8): min(8,7)*7 = 49
# Time: O(N) | Space: O(1)""", lang="Python", accent=ACCENT_CYAN))
    add(Spacer(1, 3*mm))

    # Trapping Rain Water
    add(DifficultyBadge("Trapping Rain Water", "Hard", "42"))
    add(Spacer(1, 2*mm))
    add(Paragraph(
        "<b>Problem:</b> Given elevation map, compute water trapped after it rains.<br/>"
        "<b>Key Insight:</b> Water at position i = min(max_left, max_right) - height[i]. "
        "Two-pointer approach maintains running max from each side → O(N) time, O(1) space.",
        STYLE_BODY))
    add(CodeBlock("""def trap(height):
    # Two-pointer solution: O(N) time, O(1) space
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0

    while left < right:
        if height[left] <= height[right]:
            # Right side is taller → water bounded by left_max
            if height[left] >= left_max:
                left_max = height[left]    # update max
            else:
                water += left_max - height[left]   # trap water!
            left += 1
        else:
            # Left side is taller → water bounded by right_max
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1

    return water

# Simpler to understand: prefix max arrays (O(N) space)
def trap_v2(height):
    n = len(height)
    left_max = [0]*n; right_max = [0]*n
    left_max[0] = height[0]; right_max[-1] = height[-1]
    for i in range(1, n): left_max[i] = max(left_max[i-1], height[i])
    for i in range(n-2,-1,-1): right_max[i] = max(right_max[i+1], height[i])
    return sum(min(left_max[i], right_max[i]) - height[i] for i in range(n))

print(trap([0,1,0,2,1,0,1,3,2,1,2,1]))   # 6
print(trap([4,2,0,3,2,5]))                 # 9""", lang="Python", accent=ACCENT_CYAN))
    add(Spacer(1, 3*mm))

    # Move Zeroes
    add(DifficultyBadge("Move Zeroes", "Easy", "283"))
    add(Spacer(1, 2*mm))
    add(Paragraph(
        "<b>Problem:</b> Move all 0s to end while maintaining relative order of non-zero elements. In-place.<br/>"
        "<b>Pattern:</b> Read/Write two-pointer — write pointer trails the read pointer.",
        STYLE_BODY))
    add(CodeBlock("""def moveZeroes(nums):
    write = 0   # position to write next non-zero
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write] = nums[read]
            write += 1
    # Fill rest with zeros
    while write < len(nums):
        nums[write] = 0
        write += 1

# Optimized: swap instead of overwrite (fewer writes if many non-zeros)
def moveZeroes_v2(nums):
    write = 0
    for read in range(len(nums)):
        if nums[read] != 0:
            nums[write], nums[read] = nums[read], nums[write]
            write += 1

nums = [0,1,0,3,12]
moveZeroes(nums)
print(nums)   # [1,3,12,0,0]
# Time: O(N) | Space: O(1) — true in-place""", lang="Python", accent=ACCENT_CYAN))

    add(Spacer(1, 4*mm))
    add(InsightBox("Chapter Summary",
        "Two Pointers is the pattern for sorted-array pair/triplet problems and in-place array manipulation. "
        "The key question to always ask: 'Is the array sorted or can I sort it?' Sorting costs O(N log N) "
        "but enables O(N) solutions that beat the O(N²) brute force.",
        ACCENT_CYAN))
    add(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 3: TRANSFORMERS
    # ═══════════════════════════════════════════════════════════════════════════
    add(ChapterBanner("ML  ·  DAY 1–2", "Transformer Architecture Deep Dive",
                       "Attention · Multi-head · Positional encoding · Modern variants (LLaMA, GPT)",
                       ACCENT_PURPLE))
    add(Spacer(1, 6*mm))

    add(SectionHeader("  3.1  The Original Transformer (Vaswani et al. 2017)", ACCENT_PURPLE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        'The landmark paper <b>"Attention Is All You Need"</b> introduced the Transformer in 2017, '
        "replacing RNNs and LSTMs for sequence-to-sequence tasks. The original design is an "
        "<b>encoder-decoder</b> architecture for translation. Modern LLMs evolved from this.",
        STYLE_BODY))

    add(Paragraph("Architecture Variants — Know the Differences:", STYLE_SUBSECTION))
    variant_data = [
        ["Architecture", "Examples", "Use Case", "Key Property"],
        ["Encoder-Decoder", "T5, BART, original Transformer", "Translation, Summarization", "Bidirectional encoder + causal decoder"],
        ["Encoder-Only", "BERT, RoBERTa, DistilBERT", "Classification, Embeddings, NER", "Bidirectional — sees full context"],
        ["Decoder-Only", "GPT series, LLaMA, Mistral, Claude", "Text Generation, LLMs", "Causal — only attends to past tokens"],
    ]
    vt = Table(variant_data, colWidths=[(W-40*mm)*f for f in [0.22,0.28,0.28,0.22]])
    vt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT_PURPLE),
        ("TEXTCOLOR", (0,0), (-1,0), TEXT_WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BACKGROUND", (0,1), (-1,-1), CARD_BG),
        ("TEXTCOLOR", (0,1), (-1,-1), TEXT_WHITE),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("PADDING", (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [CARD_BG, colors.HexColor("#253047")]),
    ]))
    add(vt)
    add(Spacer(1, 4*mm))

    add(SectionHeader("  3.2  Attention Mechanism — The Heart of Transformers", ACCENT_PURPLE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "Attention allows every token to look at every other token and decide how much to 'attend' to it. "
        "The three ingredients are <b>Query (Q)</b>, <b>Key (K)</b>, and <b>Value (V)</b> matrices — "
        "all learned linear projections of the input embeddings.",
        STYLE_BODY))

    add(Paragraph("Intuition — The Library Analogy:", STYLE_SUBSECTION))
    add(Paragraph(
        "Imagine you walk into a library (the sequence of tokens). You have a <b>query</b> (what you're "
        "looking for). Each book has a <b>key</b> (its catalogue entry). You compute how relevant each "
        "key is to your query → that's your attention score. Then you retrieve the actual content "
        "(<b>value</b>) weighted by those scores. The output is a weighted mix of all values.",
        STYLE_BODY))

    add(CodeBlock("""import numpy as np

def scaled_dot_product_attention(Q, K, V, mask=None):
    \"\"\"
    Q: (batch, heads, seq_len, d_k)
    K: (batch, heads, seq_len, d_k)
    V: (batch, heads, seq_len, d_v)
    \"\"\"
    d_k = Q.shape[-1]

    # Step 1: Compute raw attention scores
    # Q @ K^T → (batch, heads, seq_len, seq_len)
    scores = np.matmul(Q, K.transpose(0, 1, 3, 2))

    # Step 2: Scale — CRITICAL! Without this, scores get too large
    # when d_k is big, causing softmax to saturate (vanishing gradients)
    scores = scores / np.sqrt(d_k)

    # Step 3: Apply causal mask (for decoder / GPT-style)
    if mask is not None:
        scores = scores + mask * (-1e9)   # fill -inf where masked

    # Step 4: Softmax — convert scores to probabilities
    # Each row sums to 1 (how much to attend to each token)
    exp_scores = np.exp(scores - scores.max(axis=-1, keepdims=True))
    attn_weights = exp_scores / exp_scores.sum(axis=-1, keepdims=True)

    # Step 5: Weighted sum of Values
    output = np.matmul(attn_weights, V)

    return output, attn_weights

# Formula: Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) * V
# Why sqrt(d_k) scaling?
# QK^T dot products grow with d_k in magnitude.
# Large values → softmax peaks → vanishing gradients for other tokens.
# Dividing by sqrt(d_k) keeps variance ~1 regardless of d_k.""",
                   lang="Python", accent=ACCENT_PURPLE))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  3.3  Multi-Head Attention", ACCENT_PURPLE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "Instead of one attention computation, <b>multi-head attention</b> runs H attention heads in "
        "parallel, each with different learned Q/K/V projection matrices. Each head can specialize in "
        "different linguistic patterns (one head tracks syntax, another semantics, etc.).",
        STYLE_BODY))

    add(CodeBlock("""import numpy as np

class MultiHeadAttention:
    def __init__(self, d_model, num_heads):
        self.h = num_heads
        self.d_k = d_model // num_heads   # split model dim across heads

        # Learned projections (in practice, these are weight matrices)
        # W_Q, W_K, W_V: (d_model, d_model)
        # W_O: (d_model, d_model)

    def forward(self, Q, K, V):
        batch, seq, d_model = Q.shape

        # Step 1: Linear projections → shape: (batch, seq, d_model)
        # Q_proj = Q @ W_Q, etc.

        # Step 2: Reshape for parallel heads
        # → (batch, heads, seq, d_k)
        Q = Q.reshape(batch, seq, self.h, self.d_k).transpose(0, 2, 1, 3)
        K = K.reshape(batch, seq, self.h, self.d_k).transpose(0, 2, 1, 3)
        V = V.reshape(batch, seq, self.h, self.d_k).transpose(0, 2, 1, 3)

        # Step 3: Attention on ALL heads simultaneously
        attn_output, _ = scaled_dot_product_attention(Q, K, V)

        # Step 4: Concatenate heads and project
        # → (batch, seq, h*d_k = d_model)
        attn_output = attn_output.transpose(0, 2, 1, 3).reshape(batch, seq, d_model)
        # output = attn_output @ W_O
        return attn_output

# Example dimensions (GPT-2 small):
# d_model = 768, num_heads = 12, d_k = 64 per head""",
                   lang="Python", accent=ACCENT_PURPLE))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  3.4  Positional Encodings", ACCENT_PURPLE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "Attention is <b>permutation-invariant</b> — it doesn't know token order. Positional encodings "
        "inject position information. Two main families:",
        STYLE_BODY))

    add(CodeBlock("""import numpy as np

# ── Absolute Sinusoidal Encoding (original Transformer) ──────────────────────
def sinusoidal_encoding(seq_len, d_model):
    PE = np.zeros((seq_len, d_model))
    positions = np.arange(seq_len)[:, np.newaxis]
    dims = np.arange(0, d_model, 2)
    div_term = 10000 ** (dims / d_model)

    PE[:, 0::2] = np.sin(positions / div_term)   # even dims
    PE[:, 1::2] = np.cos(positions / div_term)   # odd dims
    return PE
# Added to token embeddings: x = embedding(token) + PE[position]

# ── RoPE — Rotary Position Embedding (LLaMA, GPT-NeoX) ──────────────────────
# Instead of adding position to embeddings, RoPE ROTATES the Q and K vectors.
# The rotation angle depends on position. Relative positions appear naturally
# in the dot product → enables length extrapolation beyond training length.

def apply_rope(x, position):
    \"\"\"Simplified 2D illustration of RoPE rotation.\"\"\"
    d = x.shape[-1]
    # For each pair of dimensions, apply rotation matrix
    theta = position / (10000 ** (2 * np.arange(d//2) / d))
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    x1, x2 = x[..., ::2], x[..., 1::2]
    return np.stack([x1*cos_theta - x2*sin_theta,
                     x1*sin_theta + x2*cos_theta], axis=-1).reshape(x.shape)

# Comparison Table:
# Sinusoidal: Fixed, no training params, limited extrapolation
# Learned (GPT-2): Trained, max_seq_len fixed at training time
# RoPE (LLaMA): Rotation-based, generalizes to longer sequences
# ALiBi (BloomZ): Adds linear bias to attention scores by distance""",
                   lang="Python", accent=ACCENT_PURPLE))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  3.5  Modern Architecture Variants", ACCENT_PURPLE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "Modern LLMs like LLaMA 3, Mistral, and others improve upon the original Transformer "
        "with several key innovations:", STYLE_BODY))

    modern_data = [
        ["Innovation", "Original Transformer", "Modern LLMs (LLaMA 3)"],
        ["Attention", "Full Multi-Head Attention (MHA)", "Grouped Query Attention (GQA)"],
        ["Normalization", "Post-LN (LayerNorm after)", "Pre-LN with RMSNorm (faster)"],
        ["Activation", "ReLU in FFN", "SwiGLU (gated, better performance)"],
        ["Position", "Sinusoidal absolute", "RoPE (rotary, relative)"],
        ["Context length", "512 tokens (original)", "128K–2M tokens + FlashAttention"],
    ]
    mt = Table(modern_data, colWidths=[(W-40*mm)*f for f in [0.25,0.35,0.40]])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT_PURPLE),
        ("TEXTCOLOR", (0,0), (-1,0), TEXT_WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BACKGROUND", (0,1), (-1,-1), CARD_BG),
        ("TEXTCOLOR", (0,1), (-1,-1), TEXT_WHITE),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("PADDING", (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [CARD_BG, colors.HexColor("#253047")]),
    ]))
    add(mt)
    add(Spacer(1, 4*mm))

    add(CodeBlock("""# Grouped Query Attention (GQA) — LLaMA 3, Mistral
# Problem: KV cache grows with seq_len × n_heads → memory bottleneck
# MQA: 1 KV head shared by all Q heads (aggressive compression)
# GQA: G groups, each group shares 1 KV head (balance between MHA and MQA)

# Example: LLaMA 3 70B — 64 Q heads, 8 KV heads (groups of 8)
# KV cache reduced by 8x vs standard MHA!

class GQA:
    def __init__(self, n_heads_q=64, n_heads_kv=8):
        self.n_q = n_heads_q
        self.n_kv = n_heads_kv
        self.groups = n_heads_q // n_heads_kv   # 8 Q heads per KV head

    def forward(self, Q, K, V):
        # Q: (batch, n_q_heads, seq, d_k)
        # K, V: (batch, n_kv_heads, seq, d_k)
        # Expand K, V to match Q heads by repeating
        K = K.repeat_interleave(self.groups, dim=1)  # (batch, n_q_heads, seq, d_k)
        V = V.repeat_interleave(self.groups, dim=1)
        return scaled_dot_product_attention(Q, K, V)

# SwiGLU activation (LLaMA FFN)
# Standard FFN: FFN(x) = ReLU(xW1)W2
# SwiGLU:       FFN(x) = (Swish(xW1) ⊙ xW3)W2  — gated variant
import torch
import torch.nn.functional as F

def swiglu(x, W1, W2, W3):
    gate = F.silu(x @ W1)   # Swish = x * sigmoid(x)
    hidden = x @ W3
    return (gate * hidden) @ W2   # element-wise gate""",
                   lang="Python", accent=ACCENT_PURPLE))

    add(Spacer(1, 4*mm))
    add(InsightBox("Interview Tip",
        "For ML interviews: always start from 'Attention(Q,K,V) = softmax(QK^T / sqrt(d_k)) * V'. "
        "Explain why sqrt(d_k) scaling exists (gradient flow). Know decoder-only vs encoder-only "
        "differences. Be ready to discuss GQA and why it reduces memory (KV cache size).",
        ACCENT_PURPLE))
    add(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 4: CPYTHON INTERNALS
    # ═══════════════════════════════════════════════════════════════════════════
    add(ChapterBanner("PYTHON  ·  DAY 1–2", "CPython Internals & Memory Model",
                       "PyObject · Reference counting · pymalloc · Integer cache · Bytecode",
                       ACCENT_BLUE))
    add(Spacer(1, 6*mm))

    add(SectionHeader("  4.1  Everything is a PyObject", ACCENT_BLUE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "<b>CPython</b> is the reference implementation of Python, written in C. Every Python object — "
        "integers, strings, lists, functions, classes — is a C struct called <b>PyObject</b> living on "
        "the heap. Understanding this explains Python's behavior at a deep level.",
        STYLE_BODY))

    add(CodeBlock("""/* C definition of PyObject (simplified) */
typedef struct _object {
    Py_ssize_t  ob_refcnt;    /* Reference count — core of memory management */
    PyTypeObject *ob_type;    /* Pointer to type object (int, str, list...) */
} PyObject;

/* PyLongObject (Python int) */
typedef struct {
    PyObject ob_base;     /* includes refcnt + type */
    Py_ssize_t ob_size;   /* number of digits */
    digit ob_digit[1];    /* flexible array of digits */
} PyLongObject;

/* In Python, you can inspect this: */
import sys
x = 42
print(sys.getrefcount(x))  # reference count (usually n+1 due to getrefcount arg)
print(type(x))             # <class 'int'>
print(id(x))               # memory address of the PyObject""",
                   lang="C / Python", accent=ACCENT_BLUE))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  4.2  Reference Counting & Garbage Collection", ACCENT_BLUE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "CPython uses <b>reference counting</b> as its primary memory management strategy. "
        "Every object tracks how many references point to it. When ob_refcnt hits 0, the object "
        "is immediately deallocated. Python also has a <b>cyclic garbage collector</b> for reference cycles.",
        STYLE_BODY))

    add(CodeBlock("""import sys
import gc

# Reference counting in action
a = [1, 2, 3]
print(sys.getrefcount(a))   # 2 (a + getrefcount arg)

b = a                        # second reference
print(sys.getrefcount(a))   # 3

del b                        # remove reference
print(sys.getrefcount(a))   # back to 2

# When refcount hits 0 → __del__ is called → memory freed immediately
class Tracked:
    def __del__(self):
        print("Freed!")

obj = Tracked()
obj = None   # refcount → 0 → "Freed!" printed immediately

# ── Reference Cycles — where refcounting fails ──
a = []
b = []
a.append(b)   # a refs b
b.append(a)   # b refs a — CYCLE!
del a, del b  # both refcounts become 1 (not 0!) → memory leak!
# Python's cyclic GC (gc module) detects and collects these

gc.collect()  # manually trigger cyclic GC
print(gc.get_count())   # (gen0, gen1, gen2) collection counts""",
                   lang="Python", accent=ACCENT_BLUE))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  4.3  Memory Allocator: pymalloc", ACCENT_BLUE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "CPython uses a custom allocator called <b>pymalloc</b> for small objects (≤ 512 bytes). "
        "It maintains pools of pre-allocated memory to avoid expensive system malloc calls for "
        "every tiny object. Large objects go directly to the OS via malloc.",
        STYLE_BODY))

    add(CodeBlock("""# pymalloc hierarchy:
# Arena (256 KB) → Pool (4 KB) → Block (8–512 bytes, power of 2)
#
# Blocks: sizes 8, 16, 24, 32, ... 512 bytes
# Each pool holds blocks of ONE size class
# Arenas hold multiple pools

# You can observe pymalloc's effect with tracemalloc
import tracemalloc

tracemalloc.start()

# Allocate small objects (go through pymalloc)
small_list = [i for i in range(1000)]

snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics('lineno')[:3]:
    print(stat)

# Large object — goes to system malloc
large = bytearray(1024 * 1024)  # 1 MB → system malloc

# Memory optimization tip: __slots__ eliminates per-instance __dict__
class Regular:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Slotted:
    __slots__ = ['x', 'y']   # no __dict__ → much less memory!
    def __init__(self, x, y):
        self.x = x
        self.y = y

import sys
print(sys.getsizeof(Regular(1, 2)))    # ~48 bytes + dict overhead
print(sys.getsizeof(Slotted(1, 2)))    # ~56 bytes, but no __dict__""",
                   lang="Python", accent=ACCENT_BLUE))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  4.4  Integer Cache, String Interning & Identity vs Equality", ACCENT_BLUE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "CPython pre-allocates integers from <b>-5 to 256</b> as singletons. This means small "
        "integers are the SAME object in memory — a huge optimization since they're used everywhere. "
        "This surprises beginners but makes sense once you know the implementation.",
        STYLE_BODY))

    add(CodeBlock("""# ── Integer Cache (-5 to 256) ────────────────────────────────────────────────
a = 256; b = 256
print(a is b)    # True  — same object in cache!
print(id(a) == id(b))   # True

c = 257; d = 257
print(c is d)    # False — outside cache, new objects created
print(id(c) == id(d))   # False (may be True in REPL due to optimization)

# RULE: NEVER use `is` for integer or string equality in production!
# Always use == for value comparison
print(a == b)    # True (correct way)

# ── String Interning ──────────────────────────────────────────────────────────
# Python auto-interns strings that look like identifiers (letters, digits, _)
s1 = "hello"
s2 = "hello"
print(s1 is s2)   # True — auto-interned (implementation detail, not guaranteed)

s3 = "hello world"   # has a space — NOT auto-interned
s4 = "hello world"
print(s3 is s4)       # False (usually)

# Force interning with sys.intern
import sys
s5 = sys.intern("hello world")
s6 = sys.intern("hello world")
print(s5 is s6)   # True — both point to same object

# WHY care about interning?
# Dictionary lookups use identity check FIRST (is), then equality (==)
# Interned strings → dict lookups are faster (identity check suffices)

# ── id() and memory addresses ─────────────────────────────────────────────────
x = [1, 2, 3]
print(id(x))   # e.g., 140234567890
y = x
print(id(y) == id(x))   # True — same object
z = [1, 2, 3]
print(id(z) == id(x))   # False — different objects, same value""",
                   lang="Python", accent=ACCENT_BLUE))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  4.5  Bytecode & the dis Module", ACCENT_BLUE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "Python compiles source code to <b>bytecode</b> (stored in .pyc files) which the CPython "
        "interpreter executes. Understanding bytecode helps optimize inner loops and understand "
        "what Python 'really does' under the hood.",
        STYLE_BODY))

    add(CodeBlock("""import dis

# Example: inspect what Python does for a simple function
def add(a, b):
    return a + b

dis.dis(add)
# Output (Python 3.11+):
#   2           0 RESUME              0
#   3           2 LOAD_FAST           0 (a)   ← push 'a' onto stack
#               4 LOAD_FAST           1 (b)   ← push 'b' onto stack
#               6 BINARY_OP          0 (+)    ← pop a,b, push result
#               8 RETURN_VALUE               ← return top of stack

# Bytecode insight: Python is a STACK machine
# Each opcode operates on a value stack

# More interesting example — list comprehension vs for loop
def list_comp(n):
    return [i*2 for i in range(n)]

def for_loop(n):
    result = []
    for i in range(n):
        result.append(i*2)
    return result

# List comprehension is faster because:
# 1. Uses LIST_APPEND opcode (no attribute lookup for .append)
# 2. Runs in its own optimized code object

import timeit
n = 10000
t1 = timeit.timeit(lambda: list_comp(n), number=1000)
t2 = timeit.timeit(lambda: for_loop(n), number=1000)
print(f"List comp: {t1:.3f}s")    # e.g., 0.412s
print(f"For loop:  {t2:.3f}s")    # e.g., 0.587s — ~30% slower""",
                   lang="Python", accent=ACCENT_BLUE))

    add(Spacer(1, 4*mm))
    add(InsightBox("Interview Tip",
        "CPython questions often trip up experienced engineers. Key facts: integers -5 to 256 are "
        "singletons, use 'is' ONLY for None/True/False, Python 3.7+ dicts preserve insertion order, "
        "and list comprehensions are faster than for loops with .append() due to bytecode optimization.",
        ACCENT_BLUE))
    add(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 5: CAP THEOREM
    # ═══════════════════════════════════════════════════════════════════════════
    add(ChapterBanner("SYSTEM DESIGN  ·  DAY 1–2", "CAP Theorem & Consistency Models",
                       "CP vs AP · Consistency spectrum · PACELC · Real-world distributed systems",
                       ACCENT_ORANGE))
    add(Spacer(1, 6*mm))

    add(SectionHeader("  5.1  CAP Theorem — The Core Trade-off", ACCENT_ORANGE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "Proposed by Eric Brewer in 2000, the <b>CAP Theorem</b> states that a distributed system "
        "can guarantee at most <b>2 of 3</b> properties: <b>C</b>onsistency, <b>A</b>vailability, "
        "and <b>P</b>artition Tolerance. Since network partitions ALWAYS occur in real distributed "
        "systems, the real choice is between C and A during a partition.",
        STYLE_BODY))

    cap_data = [
        ["Property", "Definition", "What it means in practice"],
        ["Consistency (C)", "Every read sees the most recent write", "All nodes return the same data at the same time"],
        ["Availability (A)", "Every request gets a response", "The system stays operational even if some nodes fail"],
        ["Partition Tolerance (P)", "System works despite network splits", "Nodes can't communicate, but system keeps running"],
    ]
    ct = Table(cap_data, colWidths=[(W-40*mm)*f for f in [0.22,0.38,0.40]])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT_ORANGE),
        ("TEXTCOLOR", (0,0), (-1,0), TEXT_WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BACKGROUND", (0,1), (-1,-1), CARD_BG),
        ("TEXTCOLOR", (0,1), (-1,-1), TEXT_WHITE),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("PADDING", (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [CARD_BG, colors.HexColor("#253047")]),
    ]))
    add(ct)
    add(Spacer(1, 4*mm))

    add(Paragraph("CP Systems vs AP Systems — Real Examples:", STYLE_SUBSECTION))
    sys_data = [
        ["CP Systems (Consistency + Partition Tolerance)", "AP Systems (Availability + Partition Tolerance)"],
        ["ZooKeeper — distributed coordination, locks", "Cassandra — social media, time-series data"],
        ["HBase — strongly consistent writes", "DynamoDB — shopping carts, user sessions"],
        ["etcd — Kubernetes config store", "CouchDB — offline-first applications"],
        ["MongoDB (in default config)", "Riak — high-availability key-value"],
        ["Use when: financial transactions, distributed locks", "Use when: social feeds, analytics, caching"],
    ]
    st = Table(sys_data, colWidths=[(W-40*mm)*0.5]*2)
    st.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), colors.HexColor("#1e3a5f")),
        ("BACKGROUND", (1,0), (1,0), colors.HexColor("#1e3a2f")),
        ("TEXTCOLOR", (0,0), (-1,0), TEXT_WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BACKGROUND", (0,1), (0,-1), CARD_BG),
        ("BACKGROUND", (1,1), (1,-1), colors.HexColor("#152b1e")),
        ("TEXTCOLOR", (0,1), (-1,-1), TEXT_WHITE),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("PADDING", (0,0), (-1,-1), 6),
    ]))
    add(st)
    add(Spacer(1, 4*mm))

    add(SectionHeader("  5.2  Consistency Spectrum (Strong → Eventual)", ACCENT_ORANGE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "CAP's 'Consistency' is a specific formal property (linearizability). In practice, "
        "consistency is a spectrum — choosing a weaker model often gives you better performance "
        "and availability:", STYLE_BODY))

    add(CodeBlock("""# Consistency levels from strongest to weakest:

# 1. STRONG (Linearizable) ─────────────────────────────────────────────────────
# Every operation appears instantaneous. Reads always return the latest write.
# Example: Distributed bank transfer — Bob sends Alice $100.
# After the transaction completes, any read from ANY node shows the new balances.
# Cost: Requires distributed locking / consensus (Paxos, Raft) → HIGH latency.
# Used by: ZooKeeper, etcd, Google Spanner

# 2. SEQUENTIAL ────────────────────────────────────────────────────────────────
# Operations appear in some total order consistent with program order.
# All nodes see the same sequence, but not necessarily real-time.
# Weaker than linearizable → higher throughput.

# 3. CAUSAL ────────────────────────────────────────────────────────────────────
# Operations that are causally related appear in order.
# "If you see my reply, you must have seen my post."
# Unrelated operations can be reordered.
# Example: Comment threads — replies must appear after the post.

# 4. EVENTUAL ──────────────────────────────────────────────────────────────────
# Given enough time with no new updates, all replicas converge to same value.
# NO guarantee about WHEN or in WHAT ORDER reads return values.
# Example: DNS propagation — takes hours but eventually consistent.
# Used by: Cassandra (default), DynamoDB (default), S3

# Real-world scenario:
# You post a tweet (write to primary replica).
# Your friend refreshes immediately and may NOT see it yet (replica not synced).
# 1 second later: everyone sees the tweet. Eventual consistency!

# Cassandra consistency levels (tunable!):
# ONE: fastest, weakest (read from 1 replica)
# QUORUM: majority vote (N/2 + 1) — balanced
# ALL: slowest, strongest (wait for all replicas)""",
                   lang="Python / Concepts", accent=ACCENT_ORANGE))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  5.3  PACELC & Read-Your-Writes", ACCENT_ORANGE))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "CAP only describes behavior during partitions. <b>PACELC</b> extends it: "
        "if Partition → C vs A trade-off (like CAP). Else (no partition) → Latency vs Consistency. "
        "This captures the everyday trade-off even when the network is healthy.",
        STYLE_BODY))

    add(CodeBlock("""# PACELC Classification of real systems:
# System       | Partition | Else
# ─────────────|───────────|──────────────────────────────────
# DynamoDB     | PA        | EL (eventually consistent, low latency)
# Cassandra    | PA        | EL (tunable consistency)
# MongoDB      | PC        | EC (strong, higher latency)
# HBase        | PC        | EC (strong consistency guaranteed)
# Google Spanner | PC      | EC (uses atomic clocks for near-strong + low EL)

# ── Read-Your-Writes (RYW) Consistency ───────────────────────────────────────
# Guarantee: After a write, the SAME CLIENT always reads that write.
# Why it matters: User updates profile photo → still sees old photo → confusing!

# Implementation:
# Option 1: Route reads to same replica as writes (sticky sessions)
# Option 2: Track write timestamp, read from replicas that have caught up
# Example: Twitter/X uses RYW for the posting user — you see your own tweets.

# ── Monotonic Reads ───────────────────────────────────────────────────────────
# Guarantee: If you read value X at time T, you'll never read an older value.
# Without it: Reading from different replicas → data "time travels" backwards!
# Imagine: You see "100 likes", refresh and see "95 likes" → confusing!
# Implementation: Client sends last-seen version; server waits for that version.

# ── Interview Application ─────────────────────────────────────────────────────
# Q: "Design Instagram's feed"
# A: "I'll use eventual consistency for feeds — AP system.
#     But for writes (posting photos), I'll use read-your-writes consistency
#     so the poster sees their own photo immediately.
#     Monotonic reads for pagination to avoid duplicate/missing items." """,
                   lang="Concepts / Python", accent=ACCENT_ORANGE))

    add(Spacer(1, 4*mm))
    add(InsightBox("Interview Tip",
        "When designing a system, proactively state your consistency requirements: 'For user profiles "
        "I need read-your-writes. For social feeds, eventual consistency is fine — users tolerate "
        "slight delays. For payments, I need strong consistency.' This shows senior-level thinking.",
        ACCENT_ORANGE))
    add(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # CHAPTER 6: REST API DESIGN
    # ═══════════════════════════════════════════════════════════════════════════
    add(ChapterBanner("SYSTEM DESIGN  ·  DAY 1–2", "REST API Design Mastery",
                       "HTTP methods · Status codes · Versioning · Pagination · HATEOAS",
                       ACCENT_RED))
    add(Spacer(1, 6*mm))

    add(SectionHeader("  6.1  REST Constraints & HTTP Method Semantics", ACCENT_RED))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "<b>REST</b> (Representational State Transfer) is an architectural style defined by Roy Fielding "
        "in 2000. It's not a protocol — it's a set of constraints. A system that satisfies all "
        "constraints is called RESTful. The constraints enable scalability, simplicity, and modifiability.",
        STYLE_BODY))

    add(CodeBlock("""# The 6 REST Constraints:
# 1. CLIENT-SERVER: Separation of concerns. Client handles UI, server handles data.
#    → Enables independent evolution of client and server.

# 2. STATELESS: Each request contains ALL info needed to process it.
#    Server stores NO client state between requests.
#    → Enables horizontal scaling (any server can handle any request).
#    → Sessions go in client (JWT tokens) or shared cache (Redis).

# 3. CACHEABLE: Responses must declare if they're cacheable.
#    → GET responses can be cached. POST usually not.
#    Use Cache-Control, ETag, Last-Modified headers.

# 4. UNIFORM INTERFACE (most important for REST):
#    - Resource-based URLs: /users/123 (noun, not verb)
#    - Standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
#    - Self-descriptive messages (Content-Type: application/json)
#    - HATEOAS (links to related resources)

# 5. LAYERED SYSTEM: Client can't tell if it's talking to origin server or proxy.
#    → Load balancers, CDNs, API gateways are transparent.

# 6. CODE ON DEMAND (optional): Server can send executable code (JavaScript).

# ── HTTP Method Semantics ─────────────────────────────────────────────────────
# Method   | Safe? | Idempotent? | Body? | Use case
# GET      | Yes   | Yes         | No    | Retrieve resource
# POST     | No    | NO          | Yes   | Create resource, trigger action
# PUT      | No    | Yes         | Yes   | Full update (replace entire resource)
# PATCH    | No    | No          | Yes   | Partial update (change specific fields)
# DELETE   | No    | Yes         | No    | Delete resource
# HEAD     | Yes   | Yes         | No    | Like GET but response body omitted
# OPTIONS  | Yes   | Yes         | No    | Check allowed methods (CORS preflight)

# Safe: doesn't modify state (GET, HEAD, OPTIONS)
# Idempotent: multiple identical requests = same result (GET, PUT, DELETE)
# POST is NOT idempotent! Clicking submit twice → two orders!""",
                   lang="HTTP / Concepts", accent=ACCENT_RED))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  6.2  Resource Design & URL Patterns", ACCENT_RED))
    add(Spacer(1, 3*mm))

    add(CodeBlock("""# ── URL Design — Resource-First Thinking ─────────────────────────────────────

# BAD (verb-based, RPC style):
# POST /getUser
# POST /createUser
# POST /deleteUser?id=123
# POST /updateUserProfile

# GOOD (REST — noun-based, use HTTP methods for verbs):
# GET    /users              → list all users
# POST   /users              → create new user
# GET    /users/{id}         → get specific user
# PUT    /users/{id}         → full update (replace all fields)
# PATCH  /users/{id}         → partial update (only send changed fields)
# DELETE /users/{id}         → delete user

# Nested resources (relationships):
# GET  /users/{id}/posts          → posts by user
# POST /users/{id}/posts          → create post for user
# GET  /users/{id}/posts/{postId} → specific post

# Actions that don't fit CRUD (use sub-resource or query param):
# POST /users/{id}/activate          → activate account (sub-resource action)
# POST /payments/{id}/refund         → refund payment
# POST /videos/{id}/publish          → publish video

# Query parameters for filtering, sorting, searching:
# GET /users?role=admin&active=true&sort=created_at&order=desc&limit=20&page=2

# Example: Complete user API response
import json
user_response = {
    "id": "usr_123",
    "name": "Priya Sharma",
    "email": "priya@example.com",
    "role": "admin",
    "created_at": "2024-01-15T10:30:00Z",  # ISO 8601
    "updated_at": "2024-03-20T14:22:00Z",
    "_links": {                              # HATEOAS
        "self": {"href": "/users/usr_123"},
        "posts": {"href": "/users/usr_123/posts"},
        "followers": {"href": "/users/usr_123/followers"}
    }
}
print(json.dumps(user_response, indent=2))""",
                   lang="Python / REST", accent=ACCENT_RED))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  6.3  HTTP Status Codes — Complete Reference", ACCENT_RED))
    add(Spacer(1, 3*mm))

    status_data = [
        ["Code", "Name", "When to Use"],
        ["200", "OK", "Successful GET, PUT, PATCH, DELETE"],
        ["201", "Created", "Successful POST that created a resource. Include Location header."],
        ["204", "No Content", "Successful DELETE or action with no response body"],
        ["400", "Bad Request", "Invalid request syntax, missing required fields, validation error"],
        ["401", "Unauthorized", "Not authenticated. Client must login first. (Bad name — means unauthenticated)"],
        ["403", "Forbidden", "Authenticated but not authorized. You don't have permission."],
        ["404", "Not Found", "Resource doesn't exist. Also use when hiding existence (security)."],
        ["409", "Conflict", "State conflict — duplicate email, version mismatch, concurrent edit"],
        ["422", "Unprocessable Entity", "Semantic validation failed (right format, wrong values)"],
        ["429", "Too Many Requests", "Rate limit exceeded. Include Retry-After header."],
        ["500", "Internal Server Error", "Unexpected server error. Never expose stack traces."],
        ["502", "Bad Gateway", "Upstream service returned invalid response"],
        ["503", "Service Unavailable", "Server down for maintenance. Include Retry-After header."],
    ]
    sct = Table(status_data, colWidths=[(W-40*mm)*f for f in [0.08,0.22,0.70]])
    sct.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT_RED),
        ("TEXTCOLOR", (0,0), (-1,0), TEXT_WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("BACKGROUND", (0,1), (-1,-1), CARD_BG),
        ("TEXTCOLOR", (0,1), (-1,-1), TEXT_WHITE),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("PADDING", (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [CARD_BG, colors.HexColor("#2a1515")]),
        # Color code by range
        ("TEXTCOLOR", (0,1), (0,3), ACCENT_GREEN),    # 2xx green
        ("TEXTCOLOR", (0,4), (0,-1), ACCENT_RED),      # 4xx/5xx red
    ]))
    add(sct)
    add(Spacer(1, 4*mm))

    add(SectionHeader("  6.4  API Versioning Strategies", ACCENT_RED))
    add(Spacer(1, 3*mm))

    add(CodeBlock("""# ── Strategy 1: URL Path Versioning (Most Common) ────────────────────────────
# GET /api/v1/users
# GET /api/v2/users

# Pros: Visible, easily testable in browser, cache-friendly
# Cons: Not technically "pure REST" (version is not part of resource identity)
# Used by: Twitter, Stripe, GitHub (v1, v2, v3), Twilio

# ── Strategy 2: Header Versioning ─────────────────────────────────────────────
# GET /users
# X-API-Version: 2
# OR: Accept: application/vnd.myapi.v2+json

# Pros: Clean URLs, resource identity preserved
# Cons: Hidden from URL, harder to test/share, cache keys must include header

# ── Strategy 3: Query Parameter Versioning ─────────────────────────────────────
# GET /users?version=2

# Pros: Easy to implement, backward compatible
# Cons: Messy, easy to forget, caching complications

# ── Best Practice: Versioning Strategy ────────────────────────────────────────
# 1. Start with URL versioning (/v1/)
# 2. Keep old versions alive for at least 6-12 months after announcing deprecation
# 3. Use Sunset header to communicate deprecation:
#    Sunset: Sat, 31 Dec 2025 23:59:59 GMT
# 4. Never break backward compatibility within a version (additive changes only)

# Flask example: version routing
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/api/v1/users/<int:user_id>')
def get_user_v1(user_id):
    return jsonify({"id": user_id, "name": "Alice"})   # v1 response

@app.route('/api/v2/users/<int:user_id>')
def get_user_v2(user_id):
    return jsonify({                    # v2 adds profile, links
        "id": user_id,
        "name": "Alice",
        "profile": {"bio": "...", "avatar": "..."},
        "_links": {"self": f"/api/v2/users/{user_id}"}
    })""", lang="Python / HTTP", accent=ACCENT_RED))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  6.5  Pagination Strategies", ACCENT_RED))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "Never return unbounded lists — always paginate. Three strategies, each with different "
        "trade-offs:", STYLE_BODY))

    add(CodeBlock("""# ── Strategy 1: Offset Pagination ────────────────────────────────────────────
# GET /posts?offset=20&limit=10   (skip 20, take 10)
# Simple SQL: SELECT * FROM posts ORDER BY created_at LIMIT 10 OFFSET 20

# Pros: Jump to any page, easy to implement
# Cons: "Page drift" — if items inserted/deleted between requests,
#        you skip or duplicate items. Also slow on large offsets (DB scans all rows).
# Use for: Admin interfaces, small datasets, finite data

# ── Strategy 2: Cursor-Based Pagination ────────────────────────────────────────
# GET /posts?cursor=eyJpZCI6MTIzfQ&limit=10
# cursor = base64({"id": last_seen_id})

# Pros: No page drift! Handles insertions/deletions correctly.
#        Constant time (uses indexed column for WHERE clause)
# Cons: Can't jump to arbitrary page. Cursor must be opaque to client.
# Use for: Infinite scroll feeds, real-time data (Twitter timeline, Instagram)

def get_posts_cursor(cursor, limit=10):
    import base64, json
    last_id = 0
    if cursor:
        last_id = json.loads(base64.b64decode(cursor))["id"]
    # Efficient: uses index on id
    posts = db.query("SELECT * FROM posts WHERE id > ? ORDER BY id LIMIT ?",
                     last_id, limit + 1)
    has_next = len(posts) > limit
    posts = posts[:limit]
    next_cursor = None
    if has_next:
        next_cursor = base64.b64encode(
            json.dumps({"id": posts[-1]["id"]}).encode()
        ).decode()
    return {"data": posts, "next_cursor": next_cursor, "has_next": has_next}

# Response shape:
# {
#   "data": [...],
#   "pagination": {
#     "next_cursor": "eyJpZCI6MTMzfQ==",
#     "has_next": true,
#     "limit": 10
#   }
# }

# ── Strategy 3: Keyset Pagination ────────────────────────────────────────────
# Like cursor, but uses natural DB keys directly (no encoding)
# GET /posts?after_id=133&limit=10
# SELECT * FROM posts WHERE id > 133 ORDER BY id LIMIT 10""",
                   lang="Python / SQL", accent=ACCENT_RED))
    add(Spacer(1, 3*mm))

    add(SectionHeader("  6.6  HATEOAS & Richardson Maturity Model", ACCENT_RED))
    add(Spacer(1, 3*mm))
    add(Paragraph(
        "<b>HATEOAS</b> (Hypermedia As The Engine Of Application State) means the API response includes "
        "links to related actions and resources. A fully HATEOAS API is self-discoverable — clients "
        "don't need to hard-code URLs. The <b>Richardson Maturity Model</b> measures REST compliance:",
        STYLE_BODY))

    rmm_data = [
        ["Level", "Name", "Description", "Example"],
        ["0", "The Swamp of POX", "Single endpoint, all POST", "POST /api → everything"],
        ["1", "Resources", "Multiple resource URIs", "GET /users, GET /posts"],
        ["2", "HTTP Verbs", "Proper HTTP methods + status codes", "GET /users/1, DELETE /users/1"],
        ["3", "Hypermedia (HATEOAS)", "Response includes navigation links", "Response has _links section"],
    ]
    rt = Table(rmm_data, colWidths=[(W-40*mm)*f for f in [0.08,0.22,0.35,0.35]])
    rt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT_RED),
        ("TEXTCOLOR", (0,0), (-1,0), TEXT_WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BACKGROUND", (0,1), (-1,-1), CARD_BG),
        ("TEXTCOLOR", (0,1), (-1,-1), TEXT_WHITE),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("PADDING", (0,0), (-1,-1), 5),
    ]))
    add(rt)
    add(Spacer(1, 3*mm))

    add(CodeBlock("""# HATEOAS example — Level 3 REST response
{
    "id": "order_456",
    "status": "pending",
    "total": 150.00,
    "items": [
        {"product_id": "prod_789", "qty": 2, "price": 75.00}
    ],
    "_links": {
        "self":    {"href": "/orders/456",         "method": "GET"},
        "cancel":  {"href": "/orders/456/cancel",  "method": "POST"},
        "payment": {"href": "/orders/456/payment", "method": "POST"},
        "items":   {"href": "/orders/456/items",   "method": "GET"},
        "customer":{"href": "/users/123",          "method": "GET"}
    }
}
# Client discovers available actions from response — no hard-coded URLs!
# If order is SHIPPED, cancel link disappears → client knows it's not allowed.
# This is HATEOAS: server drives application state via hypermedia.""",
                   lang="JSON", accent=ACCENT_RED))

    add(Spacer(1, 4*mm))
    add(InsightBox("Chapter Summary",
        "REST API design is about consistency and predictability. Use nouns for resources, HTTP verbs "
        "for actions, proper status codes for outcomes, versioning for evolution, and cursor pagination "
        "for real-time feeds. HATEOAS makes APIs self-documenting. Most production APIs reach Level 2 "
        "(HTTP Verbs) — Level 3 is aspirational but shows senior-level thinking.",
        ACCENT_RED))

    # ─────────────────────── QUICK REFERENCE PAGE ────────────────────────────
    add(PageBreak())
    add(SectionHeader("  QUICK REFERENCE — COMPLEXITY CHEAT SHEET", ACCENT_BLUE))
    add(Spacer(1, 3*mm))

    qr_data = [
        ["Operation", "Data Structure", "Time", "Notes"],
        ["Lookup / Insert / Delete", "HashMap / HashSet", "O(1) avg", "O(N) worst — hash collisions"],
        ["Two Pointers scan", "Sorted Array", "O(N)", "After O(N log N) sort"],
        ["Prefix Sum query", "Array + prefix[]", "O(1) query, O(N) build", "Space: O(N)"],
        ["Bucket Sort (top K)", "Array + buckets", "O(N)", "Frequency bounded by N"],
        ["Attention (single head)", "Sequence", "O(N²·d)", "N = seq len, d = dim"],
        ["FlashAttention", "Sequence", "O(N²) compute, O(N) mem", "Kernel fusion optimization"],
        ["Reference count check", "Python object", "O(1)", "sys.getrefcount(obj)"],
        ["Consensus (Paxos/Raft)", "Distributed system", "O(N) messages", "N = number of nodes"],
        ["Cursor pagination query", "Database", "O(log N)", "Uses index; offset is O(N)"],
    ]
    qrt = Table(qr_data, colWidths=[(W-40*mm)*f for f in [0.30,0.25,0.22,0.23]])
    qrt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT_BLUE),
        ("TEXTCOLOR", (0,0), (-1,0), TEXT_WHITE),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("BACKGROUND", (0,1), (-1,-1), CARD_BG),
        ("TEXTCOLOR", (0,1), (-1,-1), TEXT_WHITE),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("PADDING", (0,0), (-1,-1), 5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [CARD_BG, colors.HexColor("#253047")]),
    ]))
    add(qrt)
    add(Spacer(1, 5*mm))

    add(SectionHeader("  PATTERN RECOGNITION — WHEN TO USE WHAT", ACCENT_GREEN))
    add(Spacer(1, 3*mm))
    patterns = [
        ("🗺️  Use HashMap / HashSet when...", [
            "Need O(1) lookup for complements, pairs, or membership",
            "Counting frequencies (anagrams, top K, majority element)",
            "Grouping elements by a canonical key",
            "Caching results (memoization)",
        ], ACCENT_GREEN),
        ("👆  Use Two Pointers when...", [
            "Array is sorted and you need pairs/triplets summing to target",
            "In-place removal of elements with a condition",
            "Palindrome checks or symmetric comparisons",
            "Merge/squeeze operations on sorted sequences",
        ], ACCENT_CYAN),
        ("🏃  Use Fast/Slow Pointers when...", [
            "Cycle detection in linked list or array",
            "Finding the middle of a linked list in one pass",
            "Checking if number is happy (number theory cycles)",
            "Finding the start of a cycle (Floyd's algorithm)",
        ], ACCENT_PURPLE),
        ("☁️  Choose CP systems when...", [
            "Financial transactions, account balances",
            "Distributed locks, leader election",
            "Inventory management (avoid overselling)",
            "User authentication / permission checks",
        ], ACCENT_ORANGE),
        ("🌐  Choose AP systems when...", [
            "Social media feeds, timelines",
            "Shopping carts, wishlists",
            "Analytics, event logging, metrics",
            "DNS, CDN, caching layers",
        ], ACCENT_RED),
    ]

    for title, bullets, color in patterns:
        col_hex2 = color.hexval().replace("0x", "#").upper()
        add(Paragraph(f'<font color="{col_hex2}"><b>{title}</b></font>',
                       S("ptt", fontSize=11, fontName="Helvetica-Bold",
                          textColor=color, spaceBefore=6)))
        for b in bullets:
            add(Paragraph(f"      •  {b}", STYLE_BULLET))
        add(Spacer(1, 2*mm))

    add(Spacer(1, 4*mm))
    add(ColorRect(W - 40*mm, 4, ACCENT_BLUE))
    add(Spacer(1, 4*mm))
    add(Paragraph("Good luck with your interviews! 🚀  Built with dedication — Day 1 of many.",
                   S("final", fontSize=12, leading=18, textColor=TEXT_WHITE,
                      fontName="Helvetica-Bold", alignment=TA_CENTER)))

    # Build
    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_page)
    print(f"PDF created: {path}")
    return path


if __name__ == "__main__":
    build_doc()

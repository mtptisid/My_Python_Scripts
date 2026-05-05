from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import Flowable

W, H = A4
CONTENT_W = W - 28*mm

# ── COLORS ────────────────────────────────────────────────────────────────────
DARK       = colors.HexColor("#0F172A")
C_BLUE     = colors.HexColor("#2563EB")
C_GREEN    = colors.HexColor("#059669")
C_AMBER    = colors.HexColor("#D97706")
C_ROSE     = colors.HexColor("#DC2626")
C_PURPLE   = colors.HexColor("#7C3AED")
C_CYAN     = colors.HexColor("#0891B2")
C_ORANGE   = colors.HexColor("#EA580C")
C_PINK     = colors.HexColor("#DB2777")
C_TEAL     = colors.HexColor("#0D9488")
C_INDIGO   = colors.HexColor("#4338CA")
C_LIME     = colors.HexColor("#65A30D")
C_FUCHSIA  = colors.HexColor("#A21CAF")
C_RED      = colors.HexColor("#B91C1C")
C_SKY      = colors.HexColor("#0284C7")
LIGHT      = colors.HexColor("#F8FAFC")
TEXT       = colors.HexColor("#1E293B")
MUTED      = colors.HexColor("#64748B")

# ── CUSTOM FLOWABLES ──────────────────────────────────────────────────────────
class TopicHeader(Flowable):
    def __init__(self, number, title, color, width):
        super().__init__()
        self.number = number; self.title = title
        self.color = color; self.width = width; self.height = 44

    def draw(self):
        c = self.canv
        # bg
        c.setFillColor(self.color)
        c.roundRect(0, 0, self.width, self.height, 7, fill=1, stroke=0)
        # number badge
        c.setFillColor(colors.HexColor("#00000030"))
        c.roundRect(8, 8, 28, 28, 4, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(22, 20, str(self.number))
        # title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(48, 16, self.title)
        # decorative circles
        c.setFillColor(colors.HexColor("#FFFFFF18"))
        c.circle(self.width - 20, self.height/2, 30, fill=1, stroke=0)
        c.circle(self.width - 55, self.height/2, 20, fill=1, stroke=0)

class DivLine(Flowable):
    def __init__(self, width, color=colors.HexColor("#334155"), thickness=0.5):
        super().__init__()
        self.width=width; self.color=color; self.t=thickness; self.height=self.t
    def draw(self):
        self.canv.setStrokeColor(self.color); self.canv.setLineWidth(self.t)
        self.canv.line(0,0,self.width,0)

class SectionBar(Flowable):
    def __init__(self, text, color, width, icon=""):
        super().__init__()
        self.text = text; self.color = color
        self.width = width; self.height = 24; self.icon = icon

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.roundRect(0, 2, self.width, self.height-2, 4, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        label = f"  {self.icon}  {self.text}" if self.icon else f"  {self.text}"
        c.drawString(8, 9, label)

class ExampleHeader(Flowable):
    def __init__(self, num, title, difficulty, color, width):
        super().__init__()
        self.num = num; self.title = title
        self.diff = difficulty; self.color = color
        self.width = width; self.height = 30

    def draw(self):
        c = self.canv
        diff_colors = {"Easy": colors.HexColor("#16A34A"),
                       "Medium": colors.HexColor("#D97706"),
                       "Hard": colors.HexColor("#DC2626")}
        bg = colors.HexColor("#EFF6FF") if self.color == C_BLUE else colors.HexColor("#F0FDF4")
        c.setFillColor(colors.HexColor("#F1F5F9"))
        c.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=0)
        c.setStrokeColor(self.color)
        c.setLineWidth(2)
        c.line(0, 0, 0, self.height)
        c.setFillColor(self.color)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(10, 18, f"EXAMPLE {self.num}")
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(10, 6, self.title)
        # difficulty badge
        dc = diff_colors.get(self.diff, MUTED)
        badge_w = 52
        c.setFillColor(dc)
        c.roundRect(self.width - badge_w - 5, 8, badge_w, 14, 7, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(self.width - badge_w/2 - 5, 13, self.diff.upper())

# ── STYLES ────────────────────────────────────────────────────────────────────
def safe(text):
    """Escape special XML chars for ReportLab."""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def mk_style(name, **kw):
    return ParagraphStyle(name, **kw)

STYLES = {
    "body":    mk_style("body",    fontName="Helvetica",      fontSize=9,  textColor=TEXT,  leading=14, spaceAfter=2),
    "bold":    mk_style("bold",    fontName="Helvetica-Bold", fontSize=9,  textColor=TEXT,  leading=14),
    "intro":   mk_style("intro",   fontName="Helvetica",      fontSize=9.5,textColor=TEXT,  leading=15, alignment=TA_JUSTIFY),
    "bullet":  mk_style("bullet",  fontName="Helvetica",      fontSize=8.5,textColor=TEXT,  leading=13, leftIndent=10, spaceAfter=1),
    "problem": mk_style("problem", fontName="Helvetica",      fontSize=9,  textColor=colors.HexColor("#1E3A5F"), leading=14, leftIndent=4),
    "step":    mk_style("step",    fontName="Helvetica",      fontSize=8.5,textColor=TEXT,  leading=13, leftIndent=6, spaceAfter=1),
    "explain": mk_style("explain", fontName="Helvetica-Oblique",fontSize=8,textColor=MUTED, leading=12, leftIndent=8),
    "q_num":   mk_style("q_num",   fontName="Helvetica-Bold", fontSize=9,  textColor=TEXT,  leading=14),
    "q_body":  mk_style("q_body",  fontName="Helvetica",      fontSize=8.5,textColor=TEXT,  leading=13, leftIndent=6),
    "cover_t": mk_style("cover_t", fontName="Helvetica-Bold", fontSize=40, textColor=colors.white, alignment=TA_CENTER, leading=48),
    "cover_s": mk_style("cover_s", fontName="Helvetica",      fontSize=13, textColor=colors.HexColor("#93C5FD"), alignment=TA_CENTER, leading=18),
    "cover_n": mk_style("cover_n", fontName="Helvetica-Oblique",fontSize=9,textColor=colors.HexColor("#CBD5E1"), alignment=TA_CENTER, leading=13),
    "tag":     mk_style("tag",     fontName="Helvetica-Bold", fontSize=7.5,textColor=colors.white, alignment=TA_CENTER, leading=10),
    "footer":  mk_style("footer",  fontName="Helvetica",      fontSize=7,  textColor=MUTED, alignment=TA_CENTER, leading=10),
}

# ── CODE RENDERER ─────────────────────────────────────────────────────────────
def code_block(code_str, color=C_BLUE):
    """Render a Python code block as a styled table."""
    lines = code_str.split("\n")
    paras = []
    for line in lines:
        # count leading spaces for indentation
        stripped = line.rstrip()
        indent = len(stripped) - len(stripped.lstrip())
        display = stripped.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        p = Paragraph(
            display if display else "&nbsp;",
            ParagraphStyle("code", fontName="Courier", fontSize=7.5,
                           textColor=colors.HexColor("#1E3A5F"),
                           leading=11, leftIndent=indent*5)
        )
        paras.append(p)
    inner = [[p] for p in paras]
    tbl = Table(inner, colWidths=[CONTENT_W - 10])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ("BOX", (0,0), (-1,-1), 1, color),
        ("LINEBEFORE", (0,0), (0,-1), 3, color),
        ("TOPPADDING", (0,0), (-1,-1), 1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
    ]))
    return tbl

def explanation_box(lines_list, color=C_BLUE):
    """Numbered explanation steps."""
    inner = []
    for i, line in enumerate(lines_list, 1):
        inner.append([
            Paragraph(f"{i}", ParagraphStyle("n", fontName="Helvetica-Bold", fontSize=8,
                      textColor=color, alignment=TA_CENTER, leading=11)),
            Paragraph(line, STYLES["step"])
        ])
    tbl = Table(inner, colWidths=[18, CONTENT_W - 28])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#EFF6FF")),
        ("BOX", (0,0), (-1,-1), 0.5, color),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LINEBELOW", (0,0), (-1,-2), 0.3, colors.HexColor("#E2E8F0")),
    ]))
    return tbl

def practice_box(questions, color):
    """Practice questions box."""
    diff_c = {"Easy": colors.HexColor("#16A34A"), "Medium": colors.HexColor("#D97706"),
              "Hard": colors.HexColor("#DC2626"), "Medium-Hard": colors.HexColor("#C2410C")}
    rows = []
    for i, (q, diff) in enumerate(questions, 1):
        dc = diff_c.get(diff, MUTED)
        badge = Table([[Paragraph(diff, ParagraphStyle("d", fontName="Helvetica-Bold",
                        fontSize=6.5, textColor=colors.white, alignment=TA_CENTER, leading=9))]],
                      colWidths=[55])
        badge.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), dc),
            ("TOPPADDING", (0,0), (-1,-1), 2), ("BOTTOMPADDING", (0,0), (-1,-1), 2),
            ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
            ("ROUNDEDCORNERS", [4]),
        ]))
        rows.append([
            Paragraph(f"Q{i}.", ParagraphStyle("qn", fontName="Helvetica-Bold",
                      fontSize=9, textColor=color, leading=13)),
            Paragraph(q, STYLES["q_body"]),
            badge
        ])
    tbl = Table(rows, colWidths=[22, CONTENT_W - 90, 62])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#FFFBEB")),
        ("ROWBACKGROUNDS", (0,0), (-1,-1),
         [colors.HexColor("#FFFBEB"), colors.HexColor("#FEF9EC")]),
        ("BOX", (0,0), (-1,-1), 1, C_AMBER),
        ("LINEBEFORE", (0,0), (0,-1), 4, C_AMBER),
        ("LINEBELOW", (0,0), (-1,-2), 0.3, colors.HexColor("#FDE68A")),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    return tbl

def when_to_use_box(signals, color):
    items = [Paragraph(f"→  {s}", STYLES["bullet"]) for s in signals]
    inner = [[Paragraph("WHEN TO USE:", ParagraphStyle("wtu", fontName="Helvetica-Bold",
              fontSize=8, textColor=color, leading=11))]] + [[it] for it in items]
    tbl = Table(inner, colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F0FDF4")),
        ("BOX", (0,0), (-1,-1), 1, color),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ]))
    return tbl

# ── PAGE DECORATORS ───────────────────────────────────────────────────────────
def on_first(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.restoreState()

def on_later(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, H-20, W, 20, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawString(14*mm, H-13, "DSA SOLVED EXAMPLES — FAANG & MAANG Edition")
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(W-14*mm, H-13, f"Page {doc.page}")
    canvas.setStrokeColor(C_BLUE)
    canvas.setLineWidth(0.8)
    canvas.line(14*mm, 11*mm, W-14*mm, 11*mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawCentredString(W/2, 7*mm, "Study Hard  ·  Code Daily  ·  Get the Offer")
    canvas.restoreState()

# ── TOPIC BUILDER ─────────────────────────────────────────────────────────────
def build_topic(story, num, title, color, what_is, when_signals, examples, practice_qs):
    """
    examples = list of dicts:
      {title, difficulty, problem, approach_steps, code, explanation_steps, complexity}
    practice_qs = list of (question_str, difficulty_str)
    """
    story.append(TopicHeader(num, title, color, CONTENT_W))
    story.append(Spacer(1, 4*mm))

    # What is it
    story.append(SectionBar("CONCEPT OVERVIEW", color, CONTENT_W))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(what_is, STYLES["intro"]))
    story.append(Spacer(1, 3*mm))

    # When to use
    story.append(when_to_use_box(when_signals, color))
    story.append(Spacer(1, 4*mm))

    # Solved examples
    story.append(SectionBar("SOLVED EXAMPLES", color, CONTENT_W, "✅"))
    story.append(Spacer(1, 3*mm))

    for ex in examples:
        story.append(ExampleHeader(ex["num"], ex["title"], ex["difficulty"], color, CONTENT_W))
        story.append(Spacer(1, 2*mm))

        # Problem
        story.append(Paragraph("<b>Problem:</b>", STYLES["bold"]))
        story.append(Paragraph(ex["problem"], STYLES["problem"]))
        story.append(Spacer(1, 2*mm))

        # Approach
        story.append(Paragraph("<b>Approach / Intuition:</b>", STYLES["bold"]))
        for step in ex["approach"]:
            story.append(Paragraph(f"▸  {step}", STYLES["step"]))
        story.append(Spacer(1, 2*mm))

        # Code
        story.append(Paragraph("<b>Python Solution:</b>", STYLES["bold"]))
        story.append(Spacer(1,1*mm))
        story.append(code_block(ex["code"], color))
        story.append(Spacer(1, 2*mm))

        # Line-by-line explanation
        story.append(Paragraph("<b>Line-by-Line Explanation:</b>", STYLES["bold"]))
        story.append(Spacer(1,1*mm))
        story.append(explanation_box(ex["explanation"], color))
        story.append(Spacer(1, 2*mm))

        # Complexity
        cmp = ex.get("complexity", "")
        if cmp:
            cmp_tbl = Table([[
                Paragraph(f"⏱  Time: {cmp[0]}", ParagraphStyle("cx", fontName="Helvetica-Bold",
                    fontSize=8, textColor=C_GREEN, leading=11)),
                Paragraph(f"💾  Space: {cmp[1]}", ParagraphStyle("cx2", fontName="Helvetica-Bold",
                    fontSize=8, textColor=C_PURPLE, leading=11)),
            ]], colWidths=[CONTENT_W/2, CONTENT_W/2])
            cmp_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F0FDF4")),
                ("BOX",(0,0),(-1,-1),0.5,C_GREEN),
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
            ]))
            story.append(cmp_tbl)
        story.append(Spacer(1, 5*mm))

    # Practice questions
    story.append(SectionBar("YOUR TURN — PRACTICE QUESTIONS", C_AMBER, CONTENT_W, "📝"))
    story.append(Spacer(1, 2*mm))
    story.append(practice_box(practice_qs, color))
    story.append(Spacer(1, 6*mm))
    story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════════
#  ALL TOPIC DATA
# ════════════════════════════════════════════════════════════════════════════════

TOPICS = []

# ── 1. TWO POINTERS ───────────────────────────────────────────────────────────
TOPICS.append(dict(
    num=1, title="Two Pointers", color=C_BLUE,
    what_is=(
        "Two Pointers is a technique where you use two index variables that move through a data "
        "structure — usually an array or string — at different speeds or from different ends. "
        "Instead of using nested loops (O(n²)), two pointers let you process the array in a "
        "single pass (O(n)). Think of it like two runners on a track — one starts from the "
        "beginning, one from the end, and they run toward each other."
    ),
    when_signals=[
        "The problem involves a sorted array or can be solved after sorting",
        "You need to find a pair, triplet, or subsequence that meets some condition",
        "Keywords: 'find two numbers', 'reverse', 'palindrome', 'remove duplicates'",
        "You want to reduce an O(n²) brute force to O(n)",
    ],
    examples=[
        dict(
            num=1, title="Two Sum II — Sorted Array", difficulty="Easy",
            problem=(
                "Given a sorted array of integers and a target sum, return the 1-indexed positions "
                "of the two numbers that add up to the target. "
                "Example: nums=[2,7,11,15], target=9 → Output: [1,2] (because nums[0]+nums[1]=9)"
            ),
            approach=[
                "Since the array is sorted, place one pointer at the start (left=0) and one at the end (right=n-1).",
                "Calculate the sum of nums[left] + nums[right].",
                "If sum == target: found it! Return [left+1, right+1] (1-indexed).",
                "If sum < target: we need a bigger sum, so move left pointer RIGHT (left++).",
                "If sum > target: we need a smaller sum, so move right pointer LEFT (right--).",
                "Repeat until pointers meet. Since sorted, one pair is guaranteed.",
            ],
            code="""\
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1    # start pointers at both ends
    
    while left < right:               # stop when pointers meet
        current_sum = nums[left] + nums[right]
        
        if current_sum == target:
            return [left + 1, right + 1]   # 1-indexed answer
        
        elif current_sum < target:
            left += 1                  # need larger sum → move left right
        
        else:
            right -= 1                 # need smaller sum → move right left
    
    return []    # no solution found""",
            explanation=[
                "left=0, right=n-1: We start pointers at the two ends of the sorted array.",
                "while left < right: We keep going as long as pointers haven't crossed.",
                "current_sum = nums[left] + nums[right]: Compute the pair sum.",
                "If current_sum == target: Match found! Return 1-indexed positions.",
                "elif current_sum < target: Sum is too small. The only way to increase it in a sorted array is to move left pointer right (to a larger value).",
                "else: Sum is too big. Move right pointer left (to a smaller value).",
                "This avoids O(n²) brute force — each pointer moves at most n times, giving O(n) total.",
            ],
            complexity=("O(n)", "O(1)")
        ),
        dict(
            num=2, title="Container With Most Water", difficulty="Medium",
            problem=(
                "Given n vertical lines at positions 0..n-1 with heights height[i], "
                "find two lines that together with the x-axis form a container that holds the most water. "
                "Example: height=[1,8,6,2,5,4,8,3,7] → Output: 49"
            ),
            approach=[
                "The area between two lines at positions l and r is: min(height[l], height[r]) * (r - l).",
                "Start with the widest container possible: left=0, right=n-1.",
                "Compute the area for current pointers and update the maximum.",
                "To try to find a bigger area, move the pointer with the SHORTER line inward.",
                "Why? Moving the taller line inward can only decrease width without guaranteed height gain. Moving the shorter line might find a taller one.",
                "Repeat until pointers meet.",
            ],
            code="""\
def max_area(height):
    left, right = 0, len(height) - 1
    max_water = 0
    
    while left < right:
        # width = distance between lines, height = shorter line
        width = right - left
        h = min(height[left], height[right])
        max_water = max(max_water, width * h)
        
        # move the pointer with the shorter line inward
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    
    return max_water""",
            explanation=[
                "left=0, right=len-1: Start with the widest possible container.",
                "width = right - left: The horizontal distance between the two walls.",
                "h = min(height[left], height[right]): Water level is limited by the SHORTER wall.",
                "max_water = max(max_water, width * h): Update max area seen so far.",
                "if height[left] < height[right]: Left wall is shorter. Moving it right might find a taller wall and increase height. This is our only hope for improvement.",
                "else: right -= 1: Right wall is shorter or equal. Move it left.",
                "Each step, one pointer moves inward, so we do at most n iterations: O(n).",
            ],
            complexity=("O(n)", "O(1)")
        ),
    ],
    practice_qs=[
        ("Valid Palindrome: Given a string, determine if it is a palindrome after removing non-alphanumeric characters and ignoring case. Example: 'A man, a plan, a canal: Panama' → True", "Easy"),
        ("3Sum: Find all unique triplets in an array that sum to zero. Example: [-1,0,1,2,-1,-4] → [[-1,-1,2],[-1,0,1]]", "Medium"),
        ("Remove Duplicates from Sorted Array: Remove duplicates in-place from a sorted array and return the new length.", "Easy"),
        ("Trapping Rain Water: Given an array of bar heights, compute how much rainwater it can trap. Example: [0,1,0,2,1,0,1,3,2,1,2,1] → 6", "Hard"),
        ("Sort Colors (Dutch National Flag): Sort an array containing only 0s, 1s, and 2s in-place without using a sort function.", "Medium"),
    ]
))

# ── 2. SLIDING WINDOW ─────────────────────────────────────────────────────────
TOPICS.append(dict(
    num=2, title="Sliding Window", color=C_GREEN,
    what_is=(
        "Sliding Window is a variation of Two Pointers designed for contiguous subarrays or substrings. "
        "Imagine a window that slides over the array — you expand it by moving the right pointer, "
        "and shrink it by moving the left pointer when a condition is violated. "
        "This avoids recomputing from scratch for every possible window. "
        "Two types: Fixed window (window size k is constant) and Variable window (expand/shrink based on a condition)."
    ),
    when_signals=[
        "Problem mentions 'subarray', 'substring', 'contiguous' elements",
        "You need to find min/max/longest/shortest window satisfying some condition",
        "Keywords: 'at most k distinct', 'minimum window', 'longest without repeating'",
        "Brute force would be O(n²) — window usually brings it to O(n)",
    ],
    examples=[
        dict(
            num=1, title="Longest Substring Without Repeating Characters", difficulty="Medium",
            problem=(
                "Given a string s, find the length of the longest substring without repeating characters. "
                "Example: s='abcabcbb' → Output: 3 (the answer is 'abc')"
            ),
            approach=[
                "Use a variable-size sliding window with a HashSet to track characters in the current window.",
                "right pointer expands the window by adding s[right] to the set.",
                "If s[right] is already in the set (duplicate found), shrink the window from the left: remove s[left] from set, move left++.",
                "Keep shrinking until the duplicate is removed.",
                "At each step, update max_length = max(max_length, right - left + 1).",
            ],
            code="""\
def length_of_longest_substring(s):
    char_set = set()          # characters in current window
    left = 0
    max_length = 0
    
    for right in range(len(s)):
        # shrink window from left until no duplicate
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        
        # now s[right] is not in set — safe to add
        char_set.add(s[right])
        
        # update max window size
        max_length = max(max_length, right - left + 1)
    
    return max_length""",
            explanation=[
                "char_set = set(): Tracks which characters are currently in our window.",
                "for right in range(len(s)): right pointer expands the window one character at a time.",
                "while s[right] in char_set: There's a duplicate! We can't expand — must shrink from left.",
                "char_set.remove(s[left]); left += 1: Remove leftmost char and shrink window.",
                "char_set.add(s[right]): Now s[right] is unique in the window — add it.",
                "max_length = max(max_length, right - left + 1): Window size is right - left + 1. Track the max.",
                "Each character is added and removed at most once → O(n) total.",
            ],
            complexity=("O(n)", "O(min(n,alphabet))")
        ),
        dict(
            num=2, title="Maximum Sum Subarray of Size K", difficulty="Easy",
            problem=(
                "Given an integer array and an integer k, find the maximum sum of any contiguous subarray of size k. "
                "Example: nums=[2,1,5,1,3,2], k=3 → Output: 9 (subarray [5,1,3])"
            ),
            approach=[
                "This is a FIXED window problem — window size is always exactly k.",
                "First, compute the sum of the first k elements.",
                "Then slide the window: add the next element (right side) and remove the oldest element (left side).",
                "Update the maximum sum at each step.",
                "This avoids recomputing the sum from scratch for every window.",
            ],
            code="""\
def max_sum_subarray(nums, k):
    # compute sum of first window
    window_sum = sum(nums[:k])
    max_sum = window_sum
    
    # slide the window from position k to end
    for i in range(k, len(nums)):
        # add new right element, remove old left element
        window_sum += nums[i] - nums[i - k]
        max_sum = max(max_sum, window_sum)
    
    return max_sum""",
            explanation=[
                "window_sum = sum(nums[:k]): Compute the sum of the very first window (first k elements).",
                "max_sum = window_sum: Initialize max with the first window.",
                "for i in range(k, len(nums)): Start from index k — this is where the sliding begins.",
                "window_sum += nums[i]: Add the new element entering the window on the right.",
                "window_sum -= nums[i - k]: Remove the element leaving the window on the left. (i-k is the leftmost element of the previous window.)",
                "max_sum = max(max_sum, window_sum): Track the maximum window sum seen.",
                "No nested loops — each element added/removed exactly once → O(n).",
            ],
            complexity=("O(n)", "O(1)")
        ),
    ],
    practice_qs=[
        ("Minimum Size Subarray Sum: Find the minimum length subarray whose sum >= target. Example: target=7, nums=[2,3,1,2,4,3] → 2 (subarray [4,3])", "Medium"),
        ("Fruit Into Baskets: Given fruit types on trees, find the longest subarray with at most 2 distinct types. Example: [1,2,1,2,3] → 4", "Medium"),
        ("Permutation In String: Given s1 and s2, return true if s2 contains a permutation of s1 as a substring.", "Medium"),
        ("Maximum Average Subarray I: Find a contiguous subarray of length k with the maximum average value.", "Easy"),
        ("Longest Repeating Character Replacement: You can replace at most k characters — find the longest substring with all same characters.", "Medium"),
    ]
))

# ── 3. PREFIX SUM ─────────────────────────────────────────────────────────────
TOPICS.append(dict(
    num=3, title="Prefix Sum", color=C_TEAL,
    what_is=(
        "Prefix Sum is a preprocessing technique where you build an auxiliary array where each element "
        "prefix[i] stores the sum of all elements from index 0 to i. Once built in O(n), "
        "any subarray sum from index l to r can be answered in O(1): sum(l,r) = prefix[r] - prefix[l-1]. "
        "It's like having a running total — you can instantly know the sum between any two checkpoints."
    ),
    when_signals=[
        "Multiple queries asking for sum of a range of the array",
        "Problems asking 'how many subarrays have sum equal to k'",
        "2D matrix range sum queries",
        "When you find yourself computing the same partial sum repeatedly",
    ],
    examples=[
        dict(
            num=1, title="Subarray Sum Equals K", difficulty="Medium",
            problem=(
                "Given an integer array and integer k, return the total number of subarrays whose sum equals k. "
                "Example: nums=[1,1,1], k=2 → Output: 2 (subarrays [1,1] starting at index 0 and 1)"
            ),
            approach=[
                "Key insight: subarray sum from index i to j = prefix[j] - prefix[i-1].",
                "We want prefix[j] - prefix[i-1] = k, which means prefix[i-1] = prefix[j] - k.",
                "As we compute the running prefix sum, check: have we seen (current_sum - k) before?",
                "Use a HashMap to store how many times each prefix sum has occurred.",
                "Initialize {0: 1} because a prefix sum of 0 exists before the array starts.",
            ],
            code="""\
from collections import defaultdict

def subarray_sum(nums, k):
    count = 0
    current_sum = 0
    # HashMap: prefix_sum → how many times seen
    prefix_count = defaultdict(int)
    prefix_count[0] = 1    # empty prefix has sum 0
    
    for num in nums:
        current_sum += num   # running prefix sum
        
        # if (current_sum - k) was seen before,
        # those indices form valid subarrays ending here
        if (current_sum - k) in prefix_count:
            count += prefix_count[current_sum - k]
        
        prefix_count[current_sum] += 1   # record this prefix sum
    
    return count""",
            explanation=[
                "prefix_count = defaultdict(int): HashMap storing how many times each prefix sum has appeared.",
                "prefix_count[0] = 1: There's one way to have prefix sum 0 — take no elements.",
                "current_sum += num: Build the running prefix sum as we scan right.",
                "current_sum - k: If this value was seen before as a prefix sum, then the subarray between that earlier index and current index sums to exactly k.",
                "count += prefix_count[current_sum - k]: Add how many times that prefix sum was seen (could be multiple).",
                "prefix_count[current_sum] += 1: Record the current prefix sum for future lookups.",
                "O(n) time — one pass with O(n) extra space for the HashMap.",
            ],
            complexity=("O(n)", "O(n)")
        ),
        dict(
            num=2, title="Range Sum Query (Immutable)", difficulty="Easy",
            problem=(
                "Design a class that can answer multiple range sum queries efficiently. "
                "sumRange(left, right) should return the sum of elements between indices left and right (inclusive). "
                "Example: nums=[-2,0,3,-5,2,-1], sumRange(0,2)=1, sumRange(2,5)=-1"
            ),
            approach=[
                "Build a prefix sum array once in O(n). prefix[i] = nums[0] + nums[1] + ... + nums[i].",
                "To get sum from l to r: if l==0, return prefix[r]. Otherwise, return prefix[r] - prefix[l-1].",
                "Each query is then answered in O(1) after the O(n) preprocessing.",
            ],
            code="""\
class NumArray:
    def __init__(self, nums):
        n = len(nums)
        self.prefix = [0] * (n + 1)  # prefix[0] = 0 (sentinel)
        
        for i in range(n):
            # prefix[i+1] = sum of nums[0..i]
            self.prefix[i + 1] = self.prefix[i] + nums[i]
    
    def sumRange(self, left, right):
        # sum from left to right (inclusive)
        # = prefix[right+1] - prefix[left]
        return self.prefix[right + 1] - self.prefix[left]

# Usage:
# obj = NumArray([-2,0,3,-5,2,-1])
# obj.sumRange(0, 2)  →  1  (−2 + 0 + 3)
# obj.sumRange(2, 5)  → -1  (3 + −5 + 2 + −1)""",
            explanation=[
                "self.prefix = [0] * (n+1): Size n+1 array. prefix[0]=0 is a sentinel to handle left=0 cleanly.",
                "self.prefix[i+1] = self.prefix[i] + nums[i]: Build cumulative sum. prefix[i+1] = sum of first i+1 elements.",
                "sumRange(left, right): We need sum of nums[left..right].",
                "return self.prefix[right+1] - self.prefix[left]: prefix[right+1] = sum of nums[0..right]. Subtracting prefix[left] = sum of nums[0..left-1] gives us nums[left..right].",
                "Build once O(n), query each time O(1). Perfect for multiple queries.",
            ],
            complexity=("O(n) build, O(1) query", "O(n)")
        ),
    ],
    practice_qs=[
        ("Find the leftmost index where the prefix sum equals the suffix sum (pivot index). Example: [1,7,3,6,5,6] → 3", "Easy"),
        ("Count subarrays with equal number of 0s and 1s. Hint: Replace 0 with -1 and find subarrays summing to 0.", "Medium"),
        ("Range Sum Query 2D (Immutable): Build a class that answers sumRegion(r1,c1,r2,c2) in O(1) after O(mn) preprocessing.", "Medium"),
        ("Continuous Subarray Sum: Return true if nums has a continuous subarray of size >= 2 whose sum is a multiple of k.", "Medium"),
    ]
))

# ── 4. BINARY SEARCH ──────────────────────────────────────────────────────────
TOPICS.append(dict(
    num=4, title="Binary Search", color=C_PURPLE,
    what_is=(
        "Binary Search finds a target in a sorted collection by repeatedly halving the search space. "
        "Each comparison eliminates HALF of the remaining elements, giving O(log n) time — "
        "dramatically faster than linear search for large arrays. "
        "Advanced usage: 'Binary Search on the Answer' — when the answer itself has a monotonic property, "
        "you can binary search on the answer space (not the array). "
        "The key insight: any time you can say 'everything left of X is false, everything right is true', binary search applies."
    ),
    when_signals=[
        "Array or search space is sorted (or can be treated as sorted)",
        "You need to find a specific value, first/last occurrence, or boundary",
        "Problem asks for minimum/maximum value that satisfies a condition",
        "Keywords: 'find minimum', 'feasibility check', 'search in rotated'",
    ],
    examples=[
        dict(
            num=1, title="Find First and Last Position of Element", difficulty="Medium",
            problem=(
                "Given a sorted array of integers and a target, find the starting and ending position of the target. "
                "Return [-1,-1] if not found. Must run in O(log n). "
                "Example: nums=[5,7,7,8,8,10], target=8 → [3,4]"
            ),
            approach=[
                "Run binary search TWICE: once to find the LEFTMOST position of target, once for RIGHTMOST.",
                "For leftmost: when nums[mid]==target, DON'T stop — record mid as answer and continue searching LEFT (high=mid-1).",
                "For rightmost: when nums[mid]==target, record mid as answer and continue searching RIGHT (low=mid+1).",
                "This ensures we find the boundary positions, not just any occurrence.",
            ],
            code="""\
def search_range(nums, target):
    def find_boundary(find_left):
        low, high = 0, len(nums) - 1
        boundary = -1
        
        while low <= high:
            mid = (low + high) // 2
            
            if nums[mid] == target:
                boundary = mid         # record this position
                if find_left:
                    high = mid - 1     # keep searching LEFT for first
                else:
                    low = mid + 1      # keep searching RIGHT for last
            
            elif nums[mid] < target:
                low = mid + 1
            else:
                high = mid - 1
        
        return boundary
    
    first = find_boundary(find_left=True)
    last  = find_boundary(find_left=False)
    return [first, last]""",
            explanation=[
                "def find_boundary(find_left): A single binary search that finds either the leftmost or rightmost position based on a flag.",
                "boundary = -1: Initialize to -1 (not found). We update it whenever we find the target.",
                "if nums[mid] == target: boundary = mid: Found the target! Record this index.",
                "if find_left: high = mid - 1: Finding leftmost? Continue searching LEFT half — maybe there's an earlier occurrence.",
                "else: low = mid + 1: Finding rightmost? Continue searching RIGHT half.",
                "elif nums[mid] < target: low = mid + 1: Target is in right half.",
                "else: high = mid - 1: Target is in left half.",
                "Two binary searches, each O(log n) → total O(log n).",
            ],
            complexity=("O(log n)", "O(1)")
        ),
        dict(
            num=2, title="Koko Eating Bananas (Search on Answer)", difficulty="Medium",
            problem=(
                "Koko has piles of bananas and h hours. She can eat k bananas/hour from one pile. "
                "Find the MINIMUM k such that she can eat all bananas in h hours. "
                "Example: piles=[3,6,7,11], h=8 → Output: 4"
            ),
            approach=[
                "This is 'Binary Search on the Answer'. We search for the minimum valid k.",
                "The answer k ranges from 1 (slowest) to max(piles) (finish any pile in 1 hour).",
                "Key insight: If k=x works (she finishes in h hours), then any k>x also works. This is monotonic → binary search applies!",
                "For a given k, compute total hours = sum(ceil(pile/k) for each pile).",
                "If total hours <= h → k is feasible, try smaller (high=mid-1). Else try larger (low=mid+1).",
            ],
            code="""\
import math

def min_eating_speed(piles, h):
    low, high = 1, max(piles)    # answer range: 1 to max pile size
    result = high                 # worst case: eat max per hour
    
    while low <= high:
        mid = (low + high) // 2   # candidate speed k
        
        # compute total hours needed at speed mid
        hours_needed = sum(math.ceil(pile / mid) for pile in piles)
        
        if hours_needed <= h:
            result = mid          # mid works! record it, try smaller
            high = mid - 1
        else:
            low = mid + 1         # mid too slow, need faster
    
    return result""",
            explanation=[
                "low=1, high=max(piles): The answer must be between 1 (very slow) and max pile (eats any pile in 1 hour).",
                "result = high: Initialize with the worst case (high always works).",
                "mid = (low+high)//2: Try the midpoint speed as our candidate.",
                "hours_needed = sum(ceil(pile/mid)): For each pile, she needs ceil(pile/mid) hours at speed mid. Sum gives total.",
                "if hours_needed <= h: Speed mid is fast enough! Record it (result=mid) and try even slower (high=mid-1).",
                "else: low = mid+1: Speed mid is too slow. Must be faster.",
                "We keep narrowing until low > high. result holds the minimum valid speed.",
            ],
            complexity=("O(n log(max_pile))", "O(1)")
        ),
    ],
    practice_qs=[
        ("Search in Rotated Sorted Array: Find target in a sorted array that was rotated at some pivot. Example: [4,5,6,7,0,1,2], target=0 → 4", "Medium"),
        ("Find Minimum in Rotated Sorted Array: Find the minimum element in a rotated sorted array in O(log n).", "Medium"),
        ("Capacity to Ship Packages Within D Days: Find minimum ship capacity to ship all packages within D days (similar to Koko).", "Medium"),
        ("Find Peak Element: An element is a peak if it is greater than its neighbors. Find any peak index in O(log n).", "Medium"),
        ("Sqrt(x): Compute the integer square root of a non-negative integer x without using sqrt().", "Easy"),
    ]
))

# ── 5. HASH MAPS & SETS ───────────────────────────────────────────────────────
TOPICS.append(dict(
    num=5, title="Hash Maps & Hash Sets", color=C_AMBER,
    what_is=(
        "A HashMap (Python dict) stores key-value pairs and allows O(1) average-time lookup, insert, and delete. "
        "A HashSet (Python set) stores unique values with O(1) lookup. "
        "The core idea: trade memory for speed. By pre-storing information in a hash table, "
        "you can answer questions instantly that would otherwise require scanning the whole array. "
        "The most common use: frequency counting, seen-before checks, grouping, and complement lookups."
    ),
    when_signals=[
        "You need to count frequencies or occurrences of elements",
        "You need to check if something has been seen before (deduplication)",
        "You need to find a complement or match (like Two Sum — find if target-num exists)",
        "You're grouping elements by some property (like anagram grouping)",
    ],
    examples=[
        dict(
            num=1, title="Group Anagrams", difficulty="Medium",
            problem=(
                "Given an array of strings, group the anagrams together. "
                "An anagram uses the same characters in different order. "
                "Example: ['eat','tea','tan','ate','nat','bat'] → [['eat','tea','ate'],['tan','nat'],['bat']]"
            ),
            approach=[
                "Two strings are anagrams if and only if their SORTED characters are identical.",
                "'eat' sorted → 'aet'. 'tea' sorted → 'aet'. Same! So they're anagrams.",
                "Use sorted characters as the HashMap KEY. All anagrams will share the same key.",
                "Group strings into lists under each key. The values of the HashMap are the groups.",
            ],
            code="""\
from collections import defaultdict

def group_anagrams(strs):
    # key: sorted characters (tuple), value: list of anagrams
    groups = defaultdict(list)
    
    for word in strs:
        # sort characters to create the canonical anagram key
        key = tuple(sorted(word))   # 'eat' → ('a','e','t')
        groups[key].append(word)
    
    return list(groups.values())

# Trace through:
# 'eat' → key=('a','e','t') → groups[('a','e','t')] = ['eat']
# 'tea' → key=('a','e','t') → groups[('a','e','t')] = ['eat','tea']
# 'tan' → key=('a','n','t') → groups[('a','n','t')] = ['tan']
# ...and so on""",
            explanation=[
                "groups = defaultdict(list): A HashMap where missing keys automatically start as empty lists.",
                "for word in strs: Process each word one by one.",
                "key = tuple(sorted(word)): Sort the characters. 'eat' → ['a','e','t'] → ('a','e','t'). All anagrams produce the SAME key.",
                "groups[key].append(word): Add the word to its anagram group.",
                "return list(groups.values()): Return all groups. Each value is a list of anagrams.",
                "Time: O(n * k log k) where n=number of words, k=max word length (due to sorting).",
            ],
            complexity=("O(n * k log k)", "O(n * k)")
        ),
        dict(
            num=2, title="Longest Consecutive Sequence", difficulty="Medium",
            problem=(
                "Given an unsorted array, find the length of the longest sequence of consecutive integers. "
                "Must run in O(n). "
                "Example: nums=[100,4,200,1,3,2] → Output: 4 (sequence 1,2,3,4)"
            ),
            approach=[
                "Put all numbers in a HashSet for O(1) lookup.",
                "For each number n, check if (n-1) is in the set. If NOT, then n is the START of a sequence.",
                "From each sequence start, count how long the consecutive chain is by checking n+1, n+2, etc.",
                "This avoids counting the same sequence multiple times.",
            ],
            code="""\
def longest_consecutive(nums):
    num_set = set(nums)    # O(1) lookup for any number
    max_length = 0
    
    for num in num_set:
        # only start counting from the beginning of a sequence
        if (num - 1) not in num_set:   # num is a sequence start
            current = num
            length = 1
            
            # extend the sequence as far as possible
            while (current + 1) in num_set:
                current += 1
                length += 1
            
            max_length = max(max_length, length)
    
    return max_length

# For [100,4,200,1,3,2]:
# num=1: 0 not in set → start counting: 1,2,3,4 → length 4
# num=4: 3 IS in set → skip (not a start)
# num=100: 99 not in set → start: only 100 → length 1""",
            explanation=[
                "num_set = set(nums): Store all numbers in a set. Lookup is O(1).",
                "for num in num_set: Iterate over unique numbers (avoid processing duplicates).",
                "if (num-1) not in num_set: This is the key optimization! Only start counting from the BEGINNING of each sequence. If num-1 exists, num is not the start.",
                "current = num, length = 1: Begin counting from this sequence start.",
                "while (current+1) in num_set: Keep extending right as long as the next integer exists.",
                "max_length = max(max_length, length): Update the overall maximum.",
                "Each number is only 'counted from' once (when it's a sequence start) → amortized O(n).",
            ],
            complexity=("O(n)", "O(n)")
        ),
    ],
    practice_qs=[
        ("Top K Frequent Elements: Return the k most frequently occurring elements. Example: [1,1,1,2,2,3], k=2 → [1,2]", "Medium"),
        ("Valid Anagram: Given two strings s and t, return true if t is an anagram of s.", "Easy"),
        ("Two Sum (Classic): Given array and target, return indices of two numbers that add up to target. Each input has exactly one solution.", "Easy"),
        ("Word Pattern: Given a pattern string and a sentence, check if the sentence follows the same bijective mapping as the pattern.", "Easy"),
        ("Isomorphic Strings: Two strings are isomorphic if the characters in one can be replaced to get the other. Return true/false.", "Easy"),
    ]
))

# ── 6. LINKED LISTS ───────────────────────────────────────────────────────────
TOPICS.append(dict(
    num=6, title="Linked Lists", color=C_ROSE,
    what_is=(
        "A Linked List is a sequence of nodes, where each node contains a value and a pointer to the next node. "
        "Unlike arrays, there's no index-based access — you must traverse from the head. "
        "Advantages: O(1) insert/delete at known positions (no shifting like arrays). "
        "Key patterns: reversal (rewire the .next pointers), fast & slow pointers (for cycle detection and midpoint finding), "
        "and the dummy head trick (simplifies edge cases). Always draw the pointers before coding."
    ),
    when_signals=[
        "Problem explicitly involves a linked list data structure",
        "You need to find a cycle, the middle, or the Nth node from the end",
        "Reversal, merging, or splitting linked lists",
        "Problems involving in-place rearrangement without extra space",
    ],
    examples=[
        dict(
            num=1, title="Reverse a Linked List", difficulty="Easy",
            problem=(
                "Given the head of a singly linked list, reverse it in-place and return the new head. "
                "Example: 1→2→3→4→5 → Output: 5→4→3→2→1"
            ),
            approach=[
                "We need to rewire each node's .next pointer to point BACKWARD.",
                "Use three pointers: prev (starts at None), curr (starts at head), next_node (saves the next).",
                "In each step: save next_node = curr.next, then flip curr.next = prev.",
                "Advance both: prev = curr, curr = next_node.",
                "When curr is None, prev is the new head.",
            ],
            code="""\
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list(head):
    prev = None        # will become the new tail → None
    curr = head        # start at current head
    
    while curr:
        next_node = curr.next   # SAVE next before we overwrite it
        curr.next = prev        # FLIP: point backward
        prev = curr             # advance prev
        curr = next_node        # advance curr (using saved next)
    
    return prev   # prev is now the new head (last node we processed)

# Trace: 1→2→3→None
# Step 1: next=2, 1.next=None, prev=1, curr=2  → None←1  2→3
# Step 2: next=3, 2.next=1,   prev=2, curr=3  → None←1←2  3
# Step 3: next=None, 3.next=2, prev=3, curr=None → 3→2→1→None""",
            explanation=[
                "prev=None: The reversed list's tail points to None. prev tracks the 'already reversed' part.",
                "curr=head: Start processing from the original head.",
                "next_node = curr.next: CRITICAL — save the next pointer BEFORE overwriting it.",
                "curr.next = prev: Flip the arrow! Point current node BACKWARD to prev.",
                "prev = curr: Move prev forward to the node we just processed.",
                "curr = next_node: Move curr forward using the saved next pointer.",
                "return prev: When curr hits None, we've processed all nodes. prev is the last node processed — the new head.",
            ],
            complexity=("O(n)", "O(1)")
        ),
        dict(
            num=2, title="Detect Cycle (Floyd's Algorithm)", difficulty="Medium",
            problem=(
                "Given the head of a linked list, return the node where the cycle begins. "
                "If no cycle, return None. "
                "Example: 3→2→0→-4→(back to 2) → Output: node with value 2"
            ),
            approach=[
                "Use Floyd's Cycle Detection (tortoise & hare): slow moves 1 step, fast moves 2 steps.",
                "If there's a cycle, fast and slow MUST meet inside the cycle.",
                "Once they meet, to find the cycle start: reset one pointer to head, keep the other at meeting point.",
                "Move both one step at a time — they meet at the cycle start. (Mathematical proof exists.)",
            ],
            code="""\
def detect_cycle(head):
    # Phase 1: Detect if cycle exists using fast/slow pointers
    slow, fast = head, head
    
    while fast and fast.next:
        slow = slow.next          # move 1 step
        fast = fast.next.next     # move 2 steps
        
        if slow == fast:          # they met → cycle exists!
            break
    else:
        return None    # fast reached None → no cycle
    
    # Phase 2: Find the cycle start
    # Reset slow to head, keep fast at meeting point
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next      # both move 1 step now
    
    return slow    # this is where the cycle starts""",
            explanation=[
                "slow, fast = head, head: Both start at head. Slow moves 1 step/iter, fast moves 2.",
                "while fast and fast.next: fast needs its next node to exist before jumping 2 steps.",
                "if slow == fast: break: They met inside the cycle. Cycle confirmed.",
                "else: return None: If the while loop exits naturally (fast is None), no cycle.",
                "slow = head: RESET slow to head. Keep fast at the meeting point.",
                "while slow != fast: Move BOTH one step at a time.",
                "return slow: The point where they meet again is the cycle start. (Math: distance from head to cycle start = distance from meeting point to cycle start.)",
            ],
            complexity=("O(n)", "O(1)")
        ),
    ],
    practice_qs=[
        ("Merge Two Sorted Lists: Merge two sorted linked lists into one sorted list and return the head.", "Easy"),
        ("Remove Nth Node From End: Remove the Nth node from the end of a linked list in one pass. Use fast/slow pointer trick.", "Medium"),
        ("Reorder List: Given 1→2→3→4→5, reorder to 1→5→2→4→3 in-place. Hint: find middle, reverse second half, merge.", "Medium"),
        ("Copy List With Random Pointer: Deep copy a linked list where each node has next and random pointers.", "Medium"),
        ("Add Two Numbers: Two numbers are stored as linked lists (digits in reverse order). Add them and return the result as a linked list.", "Medium"),
    ]
))

# ── 7. STACKS & MONOTONIC STACK ───────────────────────────────────────────────
TOPICS.append(dict(
    num=7, title="Stacks & Monotonic Stack", color=C_ORANGE,
    what_is=(
        "A Stack is a Last-In-First-Out (LIFO) structure — like a stack of plates. "
        "In Python, a regular list works perfectly as a stack (append to push, pop to pop). "
        "A Monotonic Stack is a stack where elements are always kept in sorted order (either increasing or decreasing). "
        "When a new element breaks the order, we pop elements until order is restored. "
        "This is the key technique for 'Next Greater Element' style problems — "
        "for each element, find the next element that is larger/smaller."
    ),
    when_signals=[
        "Valid parentheses / bracket matching problems",
        "'Next greater/smaller element' to the left or right",
        "Problems involving 'span', 'temperatures', 'stock prices' asking for next bigger day",
        "Undo/redo operations or evaluating expressions",
    ],
    examples=[
        dict(
            num=1, title="Daily Temperatures (Next Warmer Day)", difficulty="Medium",
            problem=(
                "Given an array of daily temperatures, return an array where answer[i] is the number of days "
                "you have to wait for a warmer temperature. If no future warmer day, answer[i]=0. "
                "Example: temps=[73,74,75,71,69,72,76,73] → [1,1,4,2,1,1,0,0]"
            ),
            approach=[
                "Use a Monotonic Decreasing Stack that stores INDICES of temperatures (not values).",
                "For each day i, while the stack is not empty AND current temp > temp at stack top index: we found the answer for the stack top!",
                "Pop that index, compute the wait = i - popped_index.",
                "Push current index onto the stack.",
                "The stack always contains indices of days waiting for a warmer day.",
            ],
            code="""\
def daily_temperatures(temps):
    n = len(temps)
    answer = [0] * n          # default: 0 (no warmer day found)
    stack = []                # monotonic decreasing stack of indices
    
    for i in range(n):
        # while stack has elements AND current temp breaks monotonicity
        while stack and temps[i] > temps[stack[-1]]:
            prev_idx = stack.pop()            # index waiting for answer
            answer[prev_idx] = i - prev_idx  # days waited
        
        stack.append(i)       # push current index (still waiting)
    
    return answer

# Trace for [73,74,75,71,69,72,76,73]:
# i=0: stack=[0]
# i=1: 74>73 → pop 0, ans[0]=1. stack=[1]
# i=2: 75>74 → pop 1, ans[1]=1. stack=[2]
# i=3: 71<75 → push. stack=[2,3]
# i=4: 69<71 → push. stack=[2,3,4]
# i=5: 72>69 → pop 4, ans[4]=1; 72>71 → pop 3, ans[3]=2. stack=[2,5]""",
            explanation=[
                "answer = [0]*n: Initialize all answers to 0 (covers days with no warmer future day).",
                "stack = []: Monotonic stack storing INDICES of days that haven't found a warmer day yet.",
                "while stack and temps[i] > temps[stack[-1]]: Current day is warmer than the day at top of stack.",
                "prev_idx = stack.pop(): That earlier day's wait is over! Pop it.",
                "answer[prev_idx] = i - prev_idx: The wait was i - prev_idx days.",
                "stack.append(i): Current day goes on stack — it's still waiting for its warmer day.",
                "After the loop, remaining indices in stack have answer 0 (already initialized).",
            ],
            complexity=("O(n)", "O(n)")
        ),
        dict(
            num=2, title="Valid Parentheses", difficulty="Easy",
            problem=(
                "Given a string of brackets '(', ')', '{', '}', '[', ']', "
                "determine if the input string is valid (correctly opened and closed in order). "
                "Example: s='()[{}]' → True.  s='(]' → False.  s='([)]' → False."
            ),
            approach=[
                "Use a stack. For every opening bracket, push it onto the stack.",
                "For every closing bracket, check if the TOP of the stack is its matching opening bracket.",
                "If yes, pop the stack (matched pair). If no, it's invalid.",
                "At the end, the stack must be empty (all brackets matched).",
            ],
            code="""\
def is_valid(s):
    stack = []
    # map each closing bracket to its matching opening bracket
    matching = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in '({[':
            stack.append(char)       # opening bracket: push
        
        elif char in ')}]':
            # closing bracket: check if top of stack matches
            if not stack or stack[-1] != matching[char]:
                return False         # no match → invalid
            stack.pop()             # matched! remove the pair
    
    return len(stack) == 0   # valid only if all brackets were matched""",
            explanation=[
                "matching = {')':'(', ...}: Dictionary that maps each closing bracket to its expected opening partner.",
                "if char in '({[': Opening bracket → just push it onto the stack.",
                "elif char in ')}]': Closing bracket — we need to validate it against the stack.",
                "if not stack: Stack is empty but we have a closing bracket → invalid (nothing to match with).",
                "stack[-1] != matching[char]: Top of stack is NOT the matching opener → invalid.",
                "stack.pop(): Top matched! Remove it — this pair is resolved.",
                "return len(stack) == 0: If stack is empty, every opener was matched with a closer → valid!",
            ],
            complexity=("O(n)", "O(n)")
        ),
    ],
    practice_qs=[
        ("Min Stack: Design a stack that supports push, pop, top, and getMin() in O(1). Hint: use a second stack to track minimums.", "Medium"),
        ("Largest Rectangle in Histogram: Given bar heights, find the largest rectangle that fits inside. This is a classic monotonic stack problem.", "Hard"),
        ("Evaluate Reverse Polish Notation: Evaluate expressions like ['2','1','+','3','*'] = 9 using a stack.", "Medium"),
        ("Decode String: Decode strings like '3[a2[c]]' → 'accaccacc' using a stack to handle nested brackets.", "Medium"),
        ("Car Fleet: N cars drive to a destination. Cars behind catch up and form fleets. Return the number of fleets at the finish.", "Medium"),
    ]
))

# ── 8. RECURSION & BACKTRACKING ───────────────────────────────────────────────
TOPICS.append(dict(
    num=8, title="Recursion & Backtracking", color=C_PINK,
    what_is=(
        "Recursion is when a function calls itself to solve a smaller version of the same problem. "
        "Every recursive solution needs two things: (1) Base Case — when to stop, (2) Recursive Case — break into smaller sub-problem. "
        "Backtracking extends recursion with a 'try and undo' mechanism: explore all possibilities, "
        "and when a path doesn't work, UNDO the last choice (backtrack) and try another. "
        "Template: Choose → Explore → Un-Choose. This generates all possible solutions systematically."
    ),
    when_signals=[
        "Generate ALL combinations, permutations, or subsets",
        "Solve constraint satisfaction problems (Sudoku, N-Queens)",
        "Tree or graph problems that require exploring multiple paths",
        "Problems with the word 'all possible', 'every', 'enumerate'",
    ],
    examples=[
        dict(
            num=1, title="Generate All Subsets (Power Set)", difficulty="Medium",
            problem=(
                "Given an integer array with unique elements, return all possible subsets. "
                "The solution set must not contain duplicate subsets. "
                "Example: nums=[1,2,3] → [[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]"
            ),
            approach=[
                "Use backtracking. At each step, decide: include nums[i] or skip it.",
                "start parameter controls where we begin to avoid duplicate subsets.",
                "For each recursive call, add the current subset to results.",
                "Try adding each number from start onwards, then recurse, then remove (backtrack).",
            ],
            code="""\
def subsets(nums):
    result = []
    
    def backtrack(start, current_subset):
        # Add a COPY of current subset to result at every call
        result.append(current_subset[:])
        
        # Try adding each remaining number
        for i in range(start, len(nums)):
            current_subset.append(nums[i])      # CHOOSE: add nums[i]
            backtrack(i + 1, current_subset)    # EXPLORE: recurse
            current_subset.pop()               # UN-CHOOSE: remove nums[i]
    
    backtrack(0, [])
    return result

# Recursion tree for [1,2,3]:
# backtrack(0,[]):    add [] → result=[[]]
#   add 1 → backtrack(1,[1]):  add [1]
#     add 2 → backtrack(2,[1,2]): add [1,2]
#       add 3 → backtrack(3,[1,2,3]): add [1,2,3]. return.
#     pop 2, add 3 → backtrack(3,[1,3]): add [1,3]. return.
#   pop 1, add 2 → backtrack(2,[2]): ... and so on""",
            explanation=[
                "result.append(current_subset[:]): Add a COPY ([:]) of the current subset. Without the copy, all entries in result would point to the same list.",
                "for i in range(start, len(nums)): Try each element from 'start' onwards. Starting from i+1 in the recursive call ensures we don't reuse elements.",
                "current_subset.append(nums[i]): CHOOSE — add this element to the current subset.",
                "backtrack(i+1, current_subset): EXPLORE — recurse with the next starting index.",
                "current_subset.pop(): UN-CHOOSE — remove the element we just added. This restores state for the next iteration.",
                "This generates 2^n subsets (each element is either included or not).",
            ],
            complexity=("O(n * 2^n)", "O(n)")
        ),
        dict(
            num=2, title="Combination Sum (Reuse Allowed)", difficulty="Medium",
            problem=(
                "Given an array of distinct integers and a target, return all unique combinations that sum to target. "
                "You may use the same integer unlimited times. "
                "Example: candidates=[2,3,6,7], target=7 → [[2,2,3],[7]]"
            ),
            approach=[
                "Backtracking with a running sum.",
                "At each step, choose a candidate and subtract it from the remaining target.",
                "We can reuse the same element, so recurse with the SAME index (not i+1).",
                "Base cases: remaining==0 → found a valid combination. remaining<0 → exceeded target, stop.",
            ],
            code="""\
def combination_sum(candidates, target):
    result = []
    
    def backtrack(start, current, remaining):
        if remaining == 0:          # found a valid combination!
            result.append(current[:])
            return
        if remaining < 0:           # exceeded target, prune this branch
            return
        
        for i in range(start, len(candidates)):
            current.append(candidates[i])         # CHOOSE
            backtrack(i, current, remaining - candidates[i])  # EXPLORE (same i = reuse allowed)
            current.pop()                         # UN-CHOOSE
    
    backtrack(0, [], target)
    return result

# For [2,3,6,7], target=7:
# Try 2: remaining=5 → try 2: remaining=3 → try 2: remaining=1 → try 2: remaining=-1 PRUNE
#                                                                  try 3: remaining=-2 PRUNE
#                                          try 3: remaining=0 → ADD [2,2,3] ✓
# Try 7: remaining=0 → ADD [7] ✓""",
            explanation=[
                "if remaining == 0: We've hit the target exactly! Add a copy of current to results.",
                "if remaining < 0: We've exceeded the target. No point continuing down this branch — return early (pruning).",
                "for i in range(start, len(candidates)): Try each candidate starting from 'start' index.",
                "current.append(candidates[i]): CHOOSE this candidate.",
                "backtrack(i, current, remaining - candidates[i]): EXPLORE. Note: i (not i+1) — allows reusing the same element.",
                "current.pop(): UN-CHOOSE — backtrack by removing the last added element.",
                "The 'start' parameter prevents going back to earlier candidates (avoids duplicates like [3,2,2] when [2,2,3] is already found).",
            ],
            complexity=("O(n^(T/min) * n)", "O(T/min depth)")
        ),
    ],
    practice_qs=[
        ("Permutations: Return all possible permutations of a unique integer array. Example: [1,2,3] → [[1,2,3],[1,3,2],[2,1,3],...]", "Medium"),
        ("Word Search: Given an m×n grid and a word, return true if the word exists in the grid (adjacent cells, no reuse). Classic backtracking.", "Medium"),
        ("N-Queens: Place N queens on an N×N chessboard so no two queens attack each other. Return all distinct solutions.", "Hard"),
        ("Palindrome Partitioning: Partition a string such that every substring in the partition is a palindrome. Return all such partitions.", "Medium"),
        ("Letter Combinations of a Phone Number: Given digits 2-9, return all possible letter combinations (like old T9 keyboard).", "Medium"),
    ]
))

# ── 9. TREES (BFS + DFS) ──────────────────────────────────────────────────────
TOPICS.append(dict(
    num=9, title="Binary Trees — DFS & BFS", color=C_INDIGO,
    what_is=(
        "A Binary Tree is a hierarchical structure where each node has at most 2 children (left and right). "
        "DFS (Depth-First Search) goes deep before wide — uses recursion or a stack. "
        "Three DFS traversals: Inorder (Left→Root→Right), Preorder (Root→Left→Right), Postorder (Left→Right→Root). "
        "BFS (Breadth-First Search) visits level by level — uses a queue. "
        "Most tree problems follow a recursive pattern: solve for left subtree, solve for right subtree, combine results."
    ),
    when_signals=[
        "Problem involves traversing, searching, or modifying a tree",
        "Level-by-level processing → BFS with a queue",
        "Any problem where solution depends on combining left and right subtree results → DFS recursion",
        "Finding paths, depths, ancestors, or checking properties (balanced, valid BST)",
    ],
    examples=[
        dict(
            num=1, title="Level Order Traversal (BFS)", difficulty="Medium",
            problem=(
                "Given the root of a binary tree, return the level-order traversal of its nodes' values "
                "(i.e., from left to right, level by level). "
                "Example: tree [3,9,20,null,null,15,7] → [[3],[9,20],[15,7]]"
            ),
            approach=[
                "BFS using a queue. Start by adding the root to the queue.",
                "At each level: note how many nodes are in the queue (this is the level size).",
                "Process exactly that many nodes, adding their children to the queue for the next level.",
                "Collect all values at each level into a sublist.",
            ],
            code="""\
from collections import deque

def level_order(root):
    if not root:
        return []
    
    result = []
    queue = deque([root])         # start BFS with root
    
    while queue:
        level_size = len(queue)   # number of nodes at current level
        level_values = []
        
        for _ in range(level_size):   # process ALL nodes at this level
            node = queue.popleft()
            level_values.append(node.val)
            
            if node.left:
                queue.append(node.left)    # add left child for next level
            if node.right:
                queue.append(node.right)   # add right child for next level
        
        result.append(level_values)   # save this level's values
    
    return result""",
            explanation=[
                "queue = deque([root]): Start with only the root. deque allows O(1) popleft (regular list pop(0) is O(n)).",
                "while queue: Continue as long as there are nodes to process.",
                "level_size = len(queue): BEFORE processing, snapshot how many nodes are at this level.",
                "for _ in range(level_size): Process exactly level_size nodes — these are all from the current level.",
                "node = queue.popleft(): Take the leftmost node (FIFO order).",
                "queue.append(node.left/right): Add children for the NEXT level iteration.",
                "result.append(level_values): Add this complete level to the result.",
            ],
            complexity=("O(n)", "O(n)")
        ),
        dict(
            num=2, title="Lowest Common Ancestor of BST", difficulty="Medium",
            problem=(
                "Given a Binary Search Tree and two nodes p and q, find their Lowest Common Ancestor (LCA). "
                "LCA is the lowest node that has both p and q as descendants. "
                "Example: BST root=6, p=2, q=8 → LCA is 6"
            ),
            approach=[
                "In a BST: left < root < right. Use this property!",
                "If both p and q are LESS than current node → LCA is in the LEFT subtree.",
                "If both p and q are GREATER than current node → LCA is in the RIGHT subtree.",
                "Otherwise (one is less, one is greater, or one equals current) → current node IS the LCA.",
            ],
            code="""\
def lowest_common_ancestor(root, p, q):
    current = root
    
    while current:
        # both nodes are in right subtree
        if p.val > current.val and q.val > current.val:
            current = current.right
        
        # both nodes are in left subtree
        elif p.val < current.val and q.val < current.val:
            current = current.left
        
        # split point: one is left, one is right (or one equals current)
        else:
            return current   # this IS the LCA
    
    return None

# Works for general Binary Tree too (with DFS), but BST allows
# this elegant O(h) iterative solution using the ordering property.""",
            explanation=[
                "while current: Traverse down the tree until we find the LCA.",
                "if p.val > current.val and q.val > current.val: Both targets are larger than current → both are in the right subtree. Go right.",
                "elif p.val < current.val and q.val < current.val: Both are smaller → both in left subtree. Go left.",
                "else: return current: The paths DIVERGE here (one goes left, one goes right) OR one of p/q equals current. This is the LCA!",
                "This uses the BST ordering property to avoid checking both subtrees.",
                "Time: O(h) where h is tree height. O(log n) for balanced BST, O(n) worst case.",
            ],
            complexity=("O(h) = O(log n) avg", "O(1)")
        ),
    ],
    practice_qs=[
        ("Invert Binary Tree: Mirror a binary tree (swap all left and right children). Example: [4,2,7,1,3,6,9] → [4,7,2,9,6,3,1]", "Easy"),
        ("Maximum Depth of Binary Tree: Return the height (maximum depth) of a binary tree using DFS recursion.", "Easy"),
        ("Validate Binary Search Tree: Given a binary tree, determine if it is a valid BST. Use min/max bounds in recursion.", "Medium"),
        ("Binary Tree Right Side View: Imagine standing to the right of the tree and looking left — return the values you see (rightmost at each level).", "Medium"),
        ("Serialize and Deserialize Binary Tree: Design an algorithm to serialize a binary tree to a string and deserialize it back.", "Hard"),
    ]
))

# ── 10. GRAPHS ────────────────────────────────────────────────────────────────
TOPICS.append(dict(
    num=10, title="Graphs — DFS, BFS & Topological Sort", color=C_CYAN,
    what_is=(
        "A Graph is a collection of nodes (vertices) connected by edges. "
        "Unlike trees, graphs can have cycles and multiple paths between nodes. "
        "Represent as adjacency list: a dict where graph[node] = [list of neighbors]. "
        "Key algorithms: DFS (explore deeply, use recursion/stack), BFS (explore layer by layer, use queue), "
        "Topological Sort (order dependencies — only for DAGs), and Union Find (group connected components efficiently). "
        "The 'visited' set is critical to avoid infinite loops in cyclic graphs."
    ),
    when_signals=[
        "Connected components, islands, regions counting",
        "Shortest path in unweighted graph → BFS",
        "Dependency ordering / prerequisite checking → Topological Sort",
        "Keywords: 'path exists', 'connected', 'reachable', 'minimum steps'",
    ],
    examples=[
        dict(
            num=1, title="Number of Islands (DFS Grid)", difficulty="Medium",
            problem=(
                "Given a 2D grid of '1's (land) and '0's (water), count the number of islands. "
                "An island is surrounded by water and formed by connecting adjacent land cells horizontally/vertically. "
                "Example: 4-row 5-col grid → Output: 3"
            ),
            approach=[
                "Treat the grid as a graph. Each '1' cell is a node connected to adjacent '1' cells.",
                "Scan every cell. When you find a '1', increment island count and run DFS to mark all connected land as visited.",
                "DFS: From current cell, visit all 4 neighbors (up/down/left/right) that are '1' and not visited.",
                "Mark visited by changing '1' to '0' (or use a visited set). This prevents counting the same island twice.",
            ],
            code="""\
def num_islands(grid):
    if not grid:
        return 0
    
    rows, cols = len(grid), len(grid[0])
    islands = 0
    
    def dfs(r, c):
        # out of bounds or water or already visited
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '0'   # mark as visited by sinking to water
        # explore all 4 directions
        dfs(r+1, c); dfs(r-1, c)
        dfs(r, c+1); dfs(r, c-1)
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':   # found unvisited land
                islands += 1
                dfs(r, c)           # sink entire island
    
    return islands""",
            explanation=[
                "rows, cols = ...: Get grid dimensions for boundary checking.",
                "def dfs(r, c): Recursive DFS from cell (r,c).",
                "if r < 0 or r >= rows or ... or grid[r][c] != '1': return: Boundary check + only proceed on unvisited land ('1').",
                "grid[r][c] = '0': Mark this cell as visited by turning it to water. Prevents revisiting.",
                "dfs(r+1,c); dfs(r-1,c); ...: Recurse in all 4 directions.",
                "for r,c in grid: Scan every cell. When '1' found (undiscovered island), increment counter and DFS to sink the whole island.",
                "Time: O(m*n) — each cell visited at most once. Space: O(m*n) for recursion stack.",
            ],
            complexity=("O(m * n)", "O(m * n)")
        ),
        dict(
            num=2, title="Course Schedule (Topological Sort / Cycle Detection)", difficulty="Medium",
            problem=(
                "There are n courses (0 to n-1). prerequisites[i]=[a,b] means you must take b before a. "
                "Determine if you can finish all courses (i.e., no circular dependency). "
                "Example: n=2, prerequisites=[[1,0]] → True (take 0 then 1)"
            ),
            approach=[
                "Model as a directed graph. If [a,b] exists, add edge b→a.",
                "A cycle means you can't finish (circular prerequisite). Goal: detect if any cycle exists.",
                "DFS approach: track 3 states for each node: 0=unvisited, 1=currently in DFS path, 2=fully processed.",
                "If during DFS we encounter a node with state 1 (currently being processed) → cycle detected!",
            ],
            code="""\
def can_finish(num_courses, prerequisites):
    # Build adjacency list
    graph = {i: [] for i in range(num_courses)}
    for course, prereq in prerequisites:
        graph[prereq].append(course)
    
    # 0=unvisited, 1=in current DFS path, 2=fully processed
    state = [0] * num_courses
    
    def has_cycle(node):
        if state[node] == 1:   # revisiting a node in current path → cycle!
            return True
        if state[node] == 2:   # already fully processed → safe, no cycle here
            return False
        
        state[node] = 1        # mark: currently processing
        for neighbor in graph[node]:
            if has_cycle(neighbor):
                return True
        state[node] = 2        # mark: fully done
        return False
    
    for course in range(num_courses):
        if has_cycle(course):
            return False   # cycle found → can't finish
    return True""",
            explanation=[
                "graph = {i: [] ...}: Build adjacency list. graph[b].append(a) for prerequisite [a,b].",
                "state = [0] * num_courses: Track state of each node: 0=unvisited, 1=in-progress, 2=done.",
                "if state[node] == 1: return True: We're revisiting a node currently on our DFS path → CYCLE!",
                "if state[node] == 2: return False: This node was already fully processed safely. No need to redo.",
                "state[node] = 1: Mark node as 'currently in DFS path'.",
                "for neighbor in graph[node]: if has_cycle(neighbor): return True: Recurse into all neighbors.",
                "state[node] = 2: All neighbors processed safely. Mark this node as done.",
            ],
            complexity=("O(V + E)", "O(V + E)")
        ),
    ],
    practice_qs=[
        ("Clone Graph: Deep copy a connected undirected graph. Each node has a value and a list of neighbors. Use DFS + HashMap.", "Medium"),
        ("Pacific Atlantic Water Flow: Find all cells from which water can flow to both the Pacific and Atlantic oceans (water flows to equal or lower cells).", "Medium"),
        ("Word Ladder: Find the shortest transformation sequence from beginWord to endWord (one letter at a time, each intermediate word must be in wordList).", "Hard"),
        ("Accounts Merge: Given a list of accounts [name, emails], merge accounts that share an email. Use Union Find or DFS.", "Medium"),
        ("Find if Path Exists in Graph: Given n nodes, edges list, source, and destination — return true if a valid path exists.", "Easy"),
    ]
))

# ── 11. HEAPS ─────────────────────────────────────────────────────────────────
TOPICS.append(dict(
    num=11, title="Heaps & Priority Queues", color=C_LIME,
    what_is=(
        "A Heap is a specialized tree that always keeps the minimum (min-heap) or maximum (max-heap) element at the root. "
        "Key operations: Insert O(log n), Extract min/max O(log n), Peek min/max O(1). "
        "Python's heapq module implements a min-heap. For max-heap, push negative values. "
        "Heaps are the go-to tool whenever you see 'K largest', 'K smallest', 'K most frequent', "
        "or need to repeatedly access the minimum/maximum efficiently."
    ),
    when_signals=[
        "'K largest', 'K smallest', 'K most frequent' — any K-related problem",
        "You need to repeatedly find and remove the minimum or maximum",
        "Merging K sorted lists or arrays",
        "Running median (find median from a data stream)",
    ],
    examples=[
        dict(
            num=1, title="Kth Largest Element in an Array", difficulty="Medium",
            problem=(
                "Given an integer array and integer k, return the kth largest element. "
                "Note: kth largest means kth in sorted descending order. "
                "Example: nums=[3,2,1,5,6,4], k=2 → Output: 5"
            ),
            approach=[
                "Use a min-heap of size k. This heap always stores the K largest elements seen so far.",
                "The TOP of the heap (minimum of the K largest) = Kth largest.",
                "For each new element: if it's larger than the heap's minimum, replace the minimum.",
                "After processing all elements, heap[0] is the Kth largest.",
            ],
            code="""\
import heapq

def find_kth_largest(nums, k):
    # min-heap of size k
    # stores the k largest elements seen so far
    heap = []
    
    for num in nums:
        heapq.heappush(heap, num)   # add element
        
        if len(heap) > k:
            heapq.heappop(heap)     # remove the smallest if heap exceeds size k
    
    # heap[0] is the smallest of the k largest = kth largest
    return heap[0]

# Alternative: Quick Select is O(n) avg but O(n^2) worst case
# Heap solution: O(n log k) time, O(k) space
# For k=2, nums=[3,2,1,5,6,4]:
# After processing: heap=[5,6] (2 largest), answer=heap[0]=5 ✓""",
            explanation=[
                "heap = []: Start with an empty min-heap.",
                "heapq.heappush(heap, num): Add the current number to the heap.",
                "if len(heap) > k: heapq.heappop(heap): When the heap grows beyond size k, remove the SMALLEST element. This ensures the heap always contains the K LARGEST elements.",
                "heap[0]: After processing all numbers, the heap contains exactly k elements. heap[0] (the minimum of those k) is the Kth largest overall.",
                "Why min-heap for K largest? Counter-intuitive but correct: we KEEP the k largest by EVICTING the smallest when we have k+1 elements.",
                "O(n log k): We process n elements, each heap operation costs O(log k).",
            ],
            complexity=("O(n log k)", "O(k)")
        ),
        dict(
            num=2, title="Merge K Sorted Lists", difficulty="Hard",
            problem=(
                "Given an array of k linked lists, each sorted in ascending order, merge them all into one sorted linked list. "
                "Example: lists=[[1,4,5],[1,3,4],[2,6]] → [1,1,2,3,4,4,5,6]"
            ),
            approach=[
                "Use a min-heap. Push the FIRST node of each list into the heap.",
                "Always pop the minimum node from the heap, add it to the result.",
                "If the popped node has a next node, push that next node into the heap.",
                "Repeat until the heap is empty.",
            ],
            code="""\
import heapq

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val; self.next = next

def merge_k_lists(lists):
    dummy = ListNode(0)     # dummy head for the result list
    current = dummy
    
    # heap entries: (node_value, index, node)
    # index breaks ties when values are equal (avoids comparing ListNode objects)
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))
    
    while heap:
        val, i, node = heapq.heappop(heap)    # get smallest
        current.next = node                    # attach to result
        current = current.next
        
        if node.next:
            # push the next node from the same list
            heapq.heappush(heap, (node.next.val, i, node.next))
    
    return dummy.next""",
            explanation=[
                "dummy = ListNode(0): Dummy head simplifies building the result list (no special case for first node).",
                "heap = []: Min-heap storing tuples (value, list_index, node).",
                "for i, node in enumerate(lists): Push the first node of each list into the heap.",
                "heapq.heappop(heap): Extracts the node with the smallest value across all lists.",
                "current.next = node: Attach this smallest node to the result list.",
                "if node.next: heapq.heappush(...): The next node in the same list is now a candidate — push it.",
                "The heap always contains at most k elements (one per list). Total operations: O(N log k) where N=total nodes.",
            ],
            complexity=("O(N log k)", "O(k)")
        ),
    ],
    practice_qs=[
        ("Top K Frequent Elements: Return k most frequent elements. Hint: use a frequency HashMap then a min-heap of size k.", "Medium"),
        ("K Closest Points to Origin: Given points on a plane, return the k closest to the origin. Use a max-heap of size k.", "Medium"),
        ("Find Median From Data Stream: Design a data structure that supports addNum() and findMedian() efficiently. Use two heaps.", "Hard"),
        ("Task Scheduler: Given tasks and a cooldown period n, find the minimum time to execute all tasks. Use a max-heap for frequencies.", "Medium"),
        ("Reorganize String: Rearrange a string so no two adjacent characters are the same. Return empty string if impossible. Use max-heap.", "Medium"),
    ]
))

# ── 12. DYNAMIC PROGRAMMING ───────────────────────────────────────────────────
TOPICS.append(dict(
    num=12, title="Dynamic Programming (DP)", color=C_FUCHSIA,
    what_is=(
        "Dynamic Programming solves problems by breaking them into overlapping subproblems and caching results to avoid recomputation. "
        "DP applies when: (1) Optimal substructure — optimal solution contains optimal solutions to subproblems, "
        "(2) Overlapping subproblems — same subproblems are solved multiple times. "
        "TWO approaches: Top-Down (memoization = recursion + cache) and Bottom-Up (tabulation = build solution from base cases up). "
        "PROCESS: Start with brute force recursion → add memoization → optimize to bottom-up table."
    ),
    when_signals=[
        "Problem asks for min/max/count/whether-possible",
        "Decisions at each step affect future decisions",
        "Keywords: 'minimum cost', 'maximum profit', 'number of ways', 'can you reach'",
        "Brute force would explore exponential possibilities (2^n or n!)",
    ],
    examples=[
        dict(
            num=1, title="Coin Change — Minimum Coins", difficulty="Medium",
            problem=(
                "Given coin denominations and a total amount, find the minimum number of coins needed to make that amount. "
                "Return -1 if impossible. Coins can be used unlimited times. "
                "Example: coins=[1,5,10,25], amount=36 → 3 (25+10+1)"
            ),
            approach=[
                "Define dp[a] = minimum coins needed to make amount a.",
                "Base case: dp[0] = 0 (need 0 coins to make amount 0).",
                "For each amount from 1 to target, try using each coin: dp[a] = min(dp[a], 1 + dp[a - coin]).",
                "Think of it as: if I use this coin, I need 1 coin PLUS minimum coins for remaining amount.",
                "Build the dp table bottom-up from amount 0 to target.",
            ],
            code="""\
def coin_change(coins, amount):
    # dp[a] = min coins to make amount a
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0    # base case: 0 coins for amount 0
    
    # fill dp table for amounts 1 to target
    for a in range(1, amount + 1):
        for coin in coins:
            if coin <= a:    # can we use this coin?
                # 1 (for this coin) + min coins for remaining (a-coin)
                dp[a] = min(dp[a], 1 + dp[a - coin])
    
    # if dp[amount] is still inf, it's impossible
    return dp[amount] if dp[amount] != float('inf') else -1

# Trace for coins=[1,5], amount=6:
# dp[0]=0
# dp[1]=min(inf, 1+dp[0])=1
# dp[5]=min(inf, 1+dp[4], 1+dp[0])=min(5, 1)=1
# dp[6]=min(inf, 1+dp[5], 1+dp[1])=min(2, 2)=2 → [5,1]""",
            explanation=[
                "dp = [inf]*(amount+1): Initialize all amounts as impossible (infinity).",
                "dp[0] = 0: Base case — making amount 0 requires 0 coins.",
                "for a in range(1, amount+1): Build the solution for each amount from 1 upwards.",
                "for coin in coins: Try using each coin denomination.",
                "if coin <= a: We can only use a coin if it doesn't exceed the current amount.",
                "dp[a] = min(dp[a], 1 + dp[a-coin]): 'Use this coin' means 1 coin + best solution for the remaining (a-coin) amount.",
                "return dp[amount] if != inf else -1: If still infinity, this amount is unreachable.",
            ],
            complexity=("O(amount * n_coins)", "O(amount)")
        ),
        dict(
            num=2, title="Longest Common Subsequence (LCS)", difficulty="Medium",
            problem=(
                "Given two strings, find the length of their longest common subsequence. "
                "A subsequence doesn't need to be contiguous. "
                "Example: text1='abcde', text2='ace' → 3 (LCS is 'ace')"
            ),
            approach=[
                "Define dp[i][j] = length of LCS of text1[0..i-1] and text2[0..j-1].",
                "If text1[i-1] == text2[j-1] (characters match): dp[i][j] = 1 + dp[i-1][j-1].",
                "If they don't match: take the max of skipping one character from either string: dp[i][j] = max(dp[i-1][j], dp[i][j-1]).",
                "Fill the 2D table row by row. Answer is dp[m][n].",
            ],
            code="""\
def longest_common_subsequence(text1, text2):
    m, n = len(text1), len(text2)
    # dp[i][j] = LCS length for text1[:i] and text2[:j]
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:      # characters match!
                dp[i][j] = 1 + dp[i-1][j-1]  # extend previous LCS
            else:
                # skip one character from either string, take best
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]

# 2D table for 'abcde' vs 'ace':
#     ''  a  c  e
# ''   0  0  0  0
# a    0  1  1  1
# b    0  1  1  1
# c    0  1  2  2
# d    0  1  2  2
# e    0  1  2  3  ← answer is dp[5][3] = 3""",
            explanation=[
                "dp = [[0]*(n+1) for _ in range(m+1)]: 2D table, size (m+1)x(n+1). Extra row/col of 0s for empty string base case.",
                "for i in range(1,m+1): for j in range(1,n+1): Fill each cell.",
                "if text1[i-1] == text2[j-1]: Characters at current positions MATCH!",
                "dp[i][j] = 1 + dp[i-1][j-1]: Extend the LCS found for the previous characters by 1.",
                "else: dp[i][j] = max(dp[i-1][j], dp[i][j-1]): No match. Try skipping text1's character (dp[i-1][j]) or text2's character (dp[i][j-1]). Take the better option.",
                "return dp[m][n]: Bottom-right cell contains the LCS of the full strings.",
            ],
            complexity=("O(m * n)", "O(m * n)")
        ),
    ],
    practice_qs=[
        ("Climbing Stairs: You can climb 1 or 2 steps at a time. How many distinct ways can you reach the top of n stairs? (This is Fibonacci!)", "Easy"),
        ("House Robber: Rob houses in a row without robbing two adjacent. Maximize the total amount. Example: [2,7,9,3,1] → 12", "Medium"),
        ("Unique Paths: A robot on an m×n grid can only move right or down. Count unique paths from top-left to bottom-right.", "Medium"),
        ("Word Break: Given a string and a dictionary of words, determine if the string can be segmented into dictionary words.", "Medium"),
        ("Edit Distance (Levenshtein): Find minimum operations (insert/delete/replace) to convert word1 to word2.", "Hard"),
    ]
))

# ── 13. GREEDY ────────────────────────────────────────────────────────────────
TOPICS.append(dict(
    num=13, title="Greedy Algorithms", color=C_SKY,
    what_is=(
        "A Greedy algorithm makes the locally optimal choice at each step, hoping to reach the global optimum. "
        "It never reconsiders past decisions (unlike DP). "
        "Greedy works when: the problem has the 'greedy choice property' — a locally optimal choice leads to a globally optimal solution. "
        "Common greedy patterns: interval scheduling (sort by end time), activity selection, jump game. "
        "If greedy doesn't obviously work, think about whether DP is needed instead."
    ),
    when_signals=[
        "Interval problems: meeting rooms, activity selection, merge intervals",
        "Jump game style: 'can you reach the end?'",
        "Problems where sorting by one criterion (start/end time, size, value) leads to an optimal solution",
        "Task scheduling / resource allocation problems",
    ],
    examples=[
        dict(
            num=1, title="Jump Game — Can You Reach the End?", difficulty="Medium",
            problem=(
                "Given an array where nums[i] is the maximum jump length from index i, "
                "determine if you can reach the last index starting from index 0. "
                "Example: nums=[2,3,1,1,4] → True.  nums=[3,2,1,0,4] → False."
            ),
            approach=[
                "Greedy: Track the farthest index we can reach at any point.",
                "For each index i, if i > max_reach (we can't even get here) → False.",
                "Otherwise, update max_reach = max(max_reach, i + nums[i]).",
                "If max_reach >= last index → True.",
            ],
            code="""\
def can_jump(nums):
    max_reach = 0     # farthest index reachable so far
    
    for i in range(len(nums)):
        if i > max_reach:        # can't reach this index → stuck!
            return False
        
        # update: from index i, we can jump up to i + nums[i]
        max_reach = max(max_reach, i + nums[i])
        
        if max_reach >= len(nums) - 1:   # can reach end!
            return True
    
    return True

# Trace for [2,3,1,1,4]:
# i=0: max_reach=max(0,0+2)=2
# i=1: 1<=2 ok, max_reach=max(2,1+3)=4
# i=2: 2<=4 ok, max_reach=max(4,2+1)=4
# max_reach(4) >= last_idx(4) → True ✓

# Trace for [3,2,1,0,4]:
# i=0: max_reach=3; i=1: max_reach=3; i=2: max_reach=3; i=3: max_reach=3
# i=4: 4 > max_reach(3) → return False ✓""",
            explanation=[
                "max_reach = 0: Initially, we can only reach index 0.",
                "for i in range(len(nums)): Visit each index in order.",
                "if i > max_reach: return False: If the current index is beyond our farthest reach, we're stuck — can't get here!",
                "max_reach = max(max_reach, i + nums[i]): From index i, we can jump up to nums[i] steps. Update farthest reachable index.",
                "if max_reach >= len(nums)-1: return True: We can reach or pass the last index. Done!",
                "The greedy insight: always track the MAXIMUM reachable index. We don't need to track the exact path.",
            ],
            complexity=("O(n)", "O(1)")
        ),
        dict(
            num=2, title="Merge Intervals", difficulty="Medium",
            problem=(
                "Given an array of intervals [[start,end],...], merge all overlapping intervals. "
                "Example: [[1,3],[2,6],[8,10],[15,18]] → [[1,6],[8,10],[15,18]]"
            ),
            approach=[
                "Sort intervals by start time.",
                "Initialize result with the first interval. Iterate through remaining intervals.",
                "If current interval overlaps with the last interval in result (current start <= result's last end): merge by extending the end.",
                "If no overlap: add current interval to result as a new interval.",
            ],
            code="""\
def merge_intervals(intervals):
    # Sort by start time
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]    # start with the first interval
    
    for start, end in intervals[1:]:
        last_end = merged[-1][1]    # end of the last merged interval
        
        if start <= last_end:       # overlap! (current start within previous interval)
            # merge: extend the end if needed
            merged[-1][1] = max(last_end, end)
        else:
            # no overlap: add as new interval
            merged.append([start, end])
    
    return merged

# Trace for [[1,3],[2,6],[8,10],[15,18]]:
# Start: merged=[[1,3]]
# [2,6]: 2<=3 overlap → merged[-1][1]=max(3,6)=6 → [[1,6]]
# [8,10]: 8>6 no overlap → [[1,6],[8,10]]
# [15,18]: 15>10 no overlap → [[1,6],[8,10],[15,18]] ✓""",
            explanation=[
                "intervals.sort(key=lambda x: x[0]): Sort by start time. This ensures we process intervals in order — a GREEDY choice.",
                "merged = [intervals[0]]: Initialize with the first interval.",
                "for start, end in intervals[1:]: Process each subsequent interval.",
                "last_end = merged[-1][1]: Get the end time of the last merged interval.",
                "if start <= last_end: OVERLAP! The current interval starts before (or when) the last one ends.",
                "merged[-1][1] = max(last_end, end): Extend the last interval's end. Use max because the new interval might be fully contained.",
                "else: merged.append([start, end]): No overlap → this is a separate interval.",
            ],
            complexity=("O(n log n)", "O(n)")
        ),
    ],
    practice_qs=[
        ("Jump Game II: Find the minimum number of jumps to reach the last index. Example: [2,3,1,1,4] → 2 (0→1→4)", "Medium"),
        ("Non-overlapping Intervals: Find the minimum number of intervals to remove to make the rest non-overlapping. Hint: sort by end time.", "Medium"),
        ("Meeting Rooms II: Given meeting time intervals, find the minimum number of conference rooms required.", "Medium"),
        ("Gas Station: Given gas[i] and cost[i] for a circular route, find the starting gas station to complete the circuit. Return -1 if impossible.", "Medium"),
        ("Partition Labels: Partition a string into as many parts as possible so each letter appears in at most one part. Return part lengths.", "Medium"),
    ]
))

# ── 14. TRIES ─────────────────────────────────────────────────────────────────
TOPICS.append(dict(
    num=14, title="Tries (Prefix Trees)", color=C_RED,
    what_is=(
        "A Trie (Prefix Tree) is a tree data structure used to efficiently store and search strings. "
        "Each node represents a character. A path from root to a leaf spells a word. "
        "Trie allows: Insert O(L), Search O(L), StartsWith O(L) — where L is the word length. "
        "This beats HashMap for prefix-related queries (HashMap can check exact match but Trie can check ALL words with a given prefix). "
        "Key use cases: autocomplete systems, spell checkers, IP routing, word games."
    ),
    when_signals=[
        "Searching for words with a common prefix (autocomplete, typeahead)",
        "Multiple string searches in a set (faster than iterating through a list)",
        "Word search in a grid with a dictionary of words",
        "Implementing spell-check or word validation",
    ],
    examples=[
        dict(
            num=1, title="Implement Trie (Prefix Tree)", difficulty="Medium",
            problem=(
                "Design a Trie data structure with: insert(word), search(word) — returns true if word exists, "
                "startsWith(prefix) — returns true if any inserted word starts with the prefix. "
                "Example: insert('apple'), search('apple')→True, search('app')→False, startsWith('app')→True"
            ),
            approach=[
                "Each TrieNode has a dictionary of children (char → TrieNode) and a boolean is_end_of_word.",
                "Insert: for each character, create a node if it doesn't exist, then move to that node. Mark last node as end of word.",
                "Search: traverse nodes for each character. If any character is missing, return False. At the end, check is_end_of_word.",
                "StartsWith: same as search but don't check is_end_of_word at the end.",
            ],
            code="""\
class TrieNode:
    def __init__(self):
        self.children = {}    # char → TrieNode
        self.is_end = False   # marks end of a complete word

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()  # create if missing
            node = node.children[char]   # move to next node
        node.is_end = True    # mark end of word
    
    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False  # character not found
            node = node.children[char]
        return node.is_end    # True only if it's a complete word
    
    def startsWith(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True    # prefix exists (don't check is_end)""",
            explanation=[
                "TrieNode: children dict maps each character to the next node. is_end marks word completion.",
                "self.root = TrieNode(): Empty root node (no character, just a starting point).",
                "insert — for char in word: Walk through each character.",
                "if char not in node.children: node.children[char] = TrieNode(): Create a new node for this character if it doesn't exist.",
                "node = node.children[char]: Move down to the next node.",
                "node.is_end = True: After all characters, mark that a word ends here.",
                "search vs startsWith: Identical traversal. The only difference is search checks node.is_end at the end, startsWith just returns True if all prefix characters are found.",
            ],
            complexity=("O(L) per operation", "O(total chars)")
        ),
        dict(
            num=2, title="Word Search II (Multiple Words in Grid)", difficulty="Hard",
            problem=(
                "Given an m×n grid of characters and a list of words, return all words found in the grid. "
                "Words must be formed by adjacent cells (horizontally/vertically), cells cannot be reused in one word. "
                "Example: board=[['o','a','a','n'],...], words=['oath','pea','eat','rain'] → ['eat','oath']"
            ),
            approach=[
                "Brute force (one DFS per word) is too slow. Instead, build a Trie from all words.",
                "Run DFS from every cell. At each step, check if the current path matches a prefix in the Trie.",
                "If it does, continue DFS. If it matches a complete word (is_end), add to results.",
                "Mark cells as visited during DFS, unmark on backtrack.",
            ],
            code="""\
def find_words(board, words):
    # Build Trie from all words
    root = TrieNode()
    for word in words:
        node = root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.word = word    # store the actual word at the end node
    
    rows, cols = len(board), len(board[0])
    result = []
    
    def dfs(r, c, node):
        char = board[r][c]
        if char not in node.children:
            return
        next_node = node.children[char]
        if next_node.is_end:
            result.append(next_node.word)
            next_node.is_end = False    # prevent duplicate adds
        
        board[r][c] = '#'    # mark visited
        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] != '#':
                dfs(nr, nc, next_node)
        board[r][c] = char   # restore (backtrack)
    
    for r in range(rows):
        for c in range(cols):
            dfs(r, c, root)
    return result""",
            explanation=[
                "Build Trie: Insert all words into the Trie. Store the full word at the terminal node.",
                "node.word = word: Saves us from reconstructing the word during DFS.",
                "def dfs(r, c, node): DFS from cell (r,c) tracking our position in the Trie.",
                "if char not in node.children: return: Current cell's character isn't a valid next character in any prefix — prune!",
                "if next_node.is_end: result.append: Found a complete word! next_node.is_end=False prevents adding duplicates.",
                "board[r][c] = '#': Mark as visited. '#' won't be in the Trie so DFS won't go there.",
                "Backtrack: restore board[r][c] after DFS so other paths can use this cell.",
            ],
            complexity=("O(M * 4 * 3^(L-1))", "O(total word chars)")
        ),
    ],
    practice_qs=[
        ("Design Add and Search Words Data Structure: Support addWord() and search() where '.' in search pattern can match any letter.", "Medium"),
        ("Replace Words: Given a dictionary of roots, replace longer words in a sentence with their root form using a Trie.", "Medium"),
        ("Longest Word in Dictionary: Find the longest word in a list such that every prefix of it is also in the list.", "Easy"),
        ("Maximum XOR of Two Numbers: Use a Bit Trie (binary trie) to find two numbers with maximum XOR in O(n) time.", "Medium"),
    ]
))

# ── 15. BIT MANIPULATION ──────────────────────────────────────────────────────
TOPICS.append(dict(
    num=15, title="Bit Manipulation", color=C_INDIGO,
    what_is=(
        "Bit manipulation works directly with the binary representation of numbers using bitwise operators. "
        "Key operators: AND (&), OR (|), XOR (^), NOT (~), Left Shift (<<), Right Shift (>>). "
        "XOR is the most powerful: x^x=0, x^0=x, and it's commutative/associative. "
        "Left shift by 1 = multiply by 2. Right shift by 1 = divide by 2. "
        "Common tricks: check if bit i is set (n & (1<<i)), set bit i (n | (1<<i)), clear bit i (n & ~(1<<i))."
    ),
    when_signals=[
        "Problems involving 'find the unique element' in a list of duplicates",
        "Counting set bits (number of 1s in binary representation)",
        "Powers of 2 checks, finding missing numbers, XOR-based tricks",
        "When constraints allow O(1) space and O(n) solutions without sorting",
    ],
    examples=[
        dict(
            num=1, title="Single Number (XOR Trick)", difficulty="Easy",
            problem=(
                "Given a non-empty array where every element appears twice except for one, find that single element. "
                "Must run in O(n) time and O(1) space. "
                "Example: nums=[4,1,2,1,2] → Output: 4"
            ),
            approach=[
                "XOR magic: a^a=0 and a^0=a. XOR is also commutative and associative.",
                "XOR all numbers together. All pairs cancel out (x^x=0). What remains is the single number.",
                "4^1^2^1^2 = 4^(1^1)^(2^2) = 4^0^0 = 4.",
            ],
            code="""\
def single_number(nums):
    result = 0
    for num in nums:
        result ^= num    # XOR with each number
    return result

# Why this works:
# 4 ^ 1 ^ 2 ^ 1 ^ 2
# = 4 ^ (1^1) ^ (2^2)   (XOR is commutative/associative)
# = 4 ^ 0    ^ 0
# = 4

# Key XOR properties:
# x ^ x = 0    (same number cancels)
# x ^ 0 = x    (XOR with 0 keeps value)
# a^b^a = b    (any pair cancels, leaving the single)""",
            explanation=[
                "result = 0: XOR identity — x^0 = x, so starting with 0 is safe.",
                "result ^= num: XOR the current number into the result.",
                "XOR is commutative (a^b = b^a) and associative (a^(b^c) = (a^b)^c) — so order doesn't matter.",
                "Every pair of identical numbers XORs to 0 (x^x=0). They cancel each other.",
                "The unpaired number XORs with 0 at the end: single^0 = single.",
                "O(n) time, O(1) space — no extra data structure needed!",
            ],
            complexity=("O(n)", "O(1)")
        ),
        dict(
            num=2, title="Count Set Bits (Hamming Weight)", difficulty="Easy",
            problem=(
                "Write a function that takes an unsigned integer and returns the number of '1' bits (Hamming weight). "
                "Example: n=11 (binary: 1011) → Output: 3"
            ),
            approach=[
                "Brian Kernighan's trick: n & (n-1) clears the RIGHTMOST set bit of n.",
                "Count how many times we can do this before n becomes 0.",
                "Each iteration removes exactly one 1 bit → we count exactly as many times as there are 1 bits.",
            ],
            code="""\
def hamming_weight(n):
    count = 0
    while n:
        n &= (n - 1)    # clear the rightmost set bit
        count += 1       # we just removed one '1' bit
    return count

# Trace for n=11 (binary: 1011):
# n=1011, n-1=1010, n&(n-1) = 1010  count=1
# n=1010, n-1=1001, n&(n-1) = 1000  count=2
# n=1000, n-1=0111, n&(n-1) = 0000  count=3
# n=0, loop ends. count=3 ✓

# Alternative (simpler to remember):
def hamming_weight_simple(n):
    return bin(n).count('1')    # Python built-in binary conversion""",
            explanation=[
                "while n: Continue while n still has any 1 bits left.",
                "n &= (n-1): The trick! n-1 flips all bits from the rightmost 1 and down. ANDing with n clears that rightmost 1.",
                "Example: n=1100, n-1=1011, n&(n-1)=1000. The rightmost 1 (at position 2) was cleared.",
                "count += 1: We just removed one 1 bit, so increment the count.",
                "return count: The number of iterations equals the number of 1 bits.",
                "This runs in O(k) where k=number of set bits, vs O(32) for checking every bit. Much faster for sparse numbers.",
            ],
            complexity=("O(k) where k=set bits", "O(1)")
        ),
    ],
    practice_qs=[
        ("Missing Number: Given [0,1,...,n] with one number missing, find it using XOR or sum formula. Example: [3,0,1] → 2", "Easy"),
        ("Power of Two: Determine if an integer is a power of 2. Use the n & (n-1) == 0 trick — powers of 2 have exactly one set bit.", "Easy"),
        ("Reverse Bits: Reverse the bits of a 32-bit unsigned integer.", "Easy"),
        ("Sum of Two Integers Without +/-: Calculate sum using only bit manipulation. Hint: XOR gives sum without carry, AND << gives carry.", "Medium"),
        ("Counting Bits: For every number from 0 to n, return the count of set bits. Return the full array. O(n) solution exists with DP.", "Easy"),
    ]
))


# ════════════════════════════════════════════════════════════════════════════════
#  COVER PAGE
# ════════════════════════════════════════════════════════════════════════════════

def build_cover(story):
    story.append(Spacer(1, 14*mm))
    story.append(Paragraph("💻", ParagraphStyle("e", fontName="Helvetica-Bold",
                  fontSize=48, alignment=TA_CENTER, leading=58)))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("DSA Solved Examples", STYLES["cover_t"]))
    story.append(Paragraph("Complete Handbook for FAANG & MAANG Interviews", STYLES["cover_s"]))
    story.append(Spacer(1, 5*mm))
    story.append(DivLine(CONTENT_W, C_BLUE, 1))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        "15 Topics  ·  30 Solved Examples  ·  Line-by-Line Explanations  ·  60+ Practice Questions",
        STYLES["cover_n"]))
    story.append(Spacer(1, 8*mm))

    topics_list = [
        "Two Pointers", "Sliding Window", "Prefix Sum", "Binary Search", "Hash Maps",
        "Linked Lists", "Stacks & Mono Stack", "Recursion & Backtrack",
        "Trees DFS/BFS", "Graphs", "Heaps", "Dynamic Programming",
        "Greedy", "Tries", "Bit Manipulation"
    ]
    topic_colors = [C_BLUE, C_GREEN, C_TEAL, C_PURPLE, C_AMBER,
                    C_ROSE, C_ORANGE, C_PINK, C_INDIGO, C_CYAN,
                    C_LIME, C_FUCHSIA, C_SKY, C_RED, C_INDIGO]

    rows = []
    row = []
    for i, (t, col) in enumerate(zip(topics_list, topic_colors)):
        tag = Table([[Paragraph(f"{i+1}. {t}", STYLES["tag"])]],
                    colWidths=[(CONTENT_W - 12)/3])
        tag.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),col),
            ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),4), ("RIGHTPADDING",(0,0),(-1,-1),4),
        ]))
        row.append(tag)
        if len(row) == 3 or i == len(topics_list)-1:
            while len(row) < 3:
                row.append(Paragraph("", STYLES["body"]))
            rows.append(row)
            row = []

    grid = Table(rows, colWidths=[(CONTENT_W)/3]*3)
    grid.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),3), ("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),2), ("RIGHTPADDING",(0,0),(-1,-1),2),
    ]))
    story.append(grid)
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(
        "For each topic: Concept explanation → Solved examples with code → Your practice questions",
        STYLES["cover_n"]))
    story.append(PageBreak())


# ════════════════════════════════════════════════════════════════════════════════
#  MAIN BUILD
# ════════════════════════════════════════════════════════════════════════════════

def build_pdf(path):
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=14*mm, rightMargin=14*mm,
        topMargin=26*mm, bottomMargin=16*mm,
        title="DSA Solved Examples — FAANG & MAANG Edition",
        author="Claude"
    )
    story = []
    build_cover(story)

    for topic in TOPICS:
        build_topic(
            story,
            num=topic["num"],
            title=topic["title"],
            color=topic["color"],
            what_is=topic["what_is"],
            when_signals=topic["when_signals"],
            examples=topic["examples"],
            practice_qs=topic["practice_qs"]
        )

    doc.build(story, onFirstPage=on_first, onLaterPages=on_later)
    print(f"PDF built: {path}")

if __name__ == "__main__":
    build_pdf("/mnt/user-data/outputs/DSA_Solved_Examples_FAANG.pdf")

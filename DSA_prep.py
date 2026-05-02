from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import Flowable

# ── Color Palette ────────────────────────────────────────────────────────────
DARK_BG      = colors.HexColor("#0F172A")   # deep navy
ACCENT_BLUE  = colors.HexColor("#3B82F6")   # vivid blue
ACCENT_GREEN = colors.HexColor("#10B981")   # emerald
ACCENT_AMBER = colors.HexColor("#F59E0B")   # amber
ACCENT_ROSE  = colors.HexColor("#F43F5E")   # rose
ACCENT_PURPLE= colors.HexColor("#8B5CF6")   # violet
LIGHT_BG     = colors.HexColor("#F8FAFC")   # near-white
CARD_BG      = colors.HexColor("#1E293B")   # slate card
TEXT_WHITE   = colors.white
TEXT_DARK    = colors.HexColor("#1E293B")
TEXT_MUTED   = colors.HexColor("#64748B")
BORDER_COLOR = colors.HexColor("#334155")

W, H = A4

# ── Custom Flowables ──────────────────────────────────────────────────────────

class ColorRect(Flowable):
    """Full-width colored rectangle, used for section headers."""
    def __init__(self, width, height, fill_color, text="", text_color=colors.white,
                 font="Helvetica-Bold", font_size=14, radius=6):
        super().__init__()
        self.width   = width
        self.height  = height
        self.fill    = fill_color
        self.text    = text
        self.tc      = text_color
        self.font    = font
        self.fs      = font_size
        self.radius  = radius

    def draw(self):
        c = self.canv
        c.setFillColor(self.fill)
        c.roundRect(0, 0, self.width, self.height, self.radius, fill=1, stroke=0)
        if self.text:
            c.setFillColor(self.tc)
            c.setFont(self.font, self.fs)
            c.drawCentredString(self.width / 2, self.height / 2 - self.fs * 0.35, self.text)

class PhaseBadge(Flowable):
    """Small pill badge for phase labels."""
    def __init__(self, text, bg, fg=colors.white, w=120, h=22, font_size=9):
        super().__init__()
        self.text = text; self.bg = bg; self.fg = fg
        self.width = w; self.height = h; self.fs = font_size

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self.width, self.height, self.height/2, fill=1, stroke=0)
        c.setFillColor(self.fg)
        c.setFont("Helvetica-Bold", self.fs)
        c.drawCentredString(self.width/2, self.height/2 - self.fs*0.35, self.text)

class DividerLine(Flowable):
    def __init__(self, width, color=BORDER_COLOR, thickness=0.5):
        super().__init__()
        self.width = width; self.color = color; self.t = thickness; self.height = self.t

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.t)
        self.canv.line(0, 0, self.width, 0)

# ── Styles ────────────────────────────────────────────────────────────────────

def make_styles():
    base = getSampleStyleSheet()

    def ps(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "cover_title": ps("cover_title",
            fontName="Helvetica-Bold", fontSize=38,
            textColor=TEXT_WHITE, alignment=TA_CENTER, leading=46,
            spaceAfter=8),
        "cover_sub": ps("cover_sub",
            fontName="Helvetica", fontSize=14,
            textColor=colors.HexColor("#93C5FD"), alignment=TA_CENTER,
            leading=20, spaceAfter=4),
        "cover_note": ps("cover_note",
            fontName="Helvetica-Oblique", fontSize=10,
            textColor=colors.HexColor("#CBD5E1"), alignment=TA_CENTER,
            leading=14),
        "section_title": ps("section_title",
            fontName="Helvetica-Bold", fontSize=15,
            textColor=TEXT_WHITE, alignment=TA_CENTER, leading=20),
        "phase_title": ps("phase_title",
            fontName="Helvetica-Bold", fontSize=13,
            textColor=TEXT_DARK, leading=18, spaceAfter=2),
        "phase_week": ps("phase_week",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=ACCENT_BLUE, leading=12, spaceAfter=4),
        "body": ps("body",
            fontName="Helvetica", fontSize=9,
            textColor=TEXT_DARK, leading=14, spaceAfter=2),
        "body_bold": ps("body_bold",
            fontName="Helvetica-Bold", fontSize=9,
            textColor=TEXT_DARK, leading=14),
        "bullet": ps("bullet",
            fontName="Helvetica", fontSize=9,
            textColor=TEXT_DARK, leading=13,
            leftIndent=12, spaceAfter=1,
            bulletIndent=2),
        "tip": ps("tip",
            fontName="Helvetica-Oblique", fontSize=8.5,
            textColor=colors.HexColor("#065F46"),  # dark-green
            leading=12),
        "concept_label": ps("concept_label",
            fontName="Helvetica-Bold", fontSize=8,
            textColor=TEXT_WHITE, alignment=TA_CENTER, leading=10),
        "footer": ps("footer",
            fontName="Helvetica", fontSize=7,
            textColor=TEXT_MUTED, alignment=TA_CENTER, leading=10),
        "toc_item": ps("toc_item",
            fontName="Helvetica", fontSize=10,
            textColor=TEXT_DARK, leading=16, leftIndent=8),
        "intro": ps("intro",
            fontName="Helvetica", fontSize=9.5,
            textColor=TEXT_DARK, leading=15, alignment=TA_JUSTIFY),
    }

# ── Helper builders ───────────────────────────────────────────────────────────

CONTENT_W = W - 30*mm   # usable width inside margins

def section_header(title, color):
    return [
        Spacer(1, 6*mm),
        ColorRect(CONTENT_W, 32, color, title, font_size=13),
        Spacer(1, 4*mm),
    ]

def phase_card(phase_num, title, weeks, color, description,
               topics, tips, example_code=""):
    """Build a phase card as a Table for visual grouping."""
    S = make_styles()

    inner = []
    inner.append(Paragraph(f"PHASE {phase_num}  ·  {weeks}", S["phase_week"]))
    inner.append(Paragraph(title, S["phase_title"]))
    inner.append(Spacer(1, 3))
    inner.append(Paragraph(description, S["intro"]))
    inner.append(Spacer(1, 4))

    # Topics as two-column tag table
    tags = []
    row = []
    for i, t in enumerate(topics):
        tag_tbl = Table([[Paragraph(t, S["concept_label"])]],
                        colWidths=[None])
        tag_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), color),
            ("ROUNDEDCORNERS", [4]),
            ("TOPPADDING", (0,0), (-1,-1), 3),
            ("BOTTOMPADDING", (0,0), (-1,-1), 3),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ]))
        row.append(tag_tbl)
        if len(row) == 4 or i == len(topics)-1:
            while len(row) < 4:
                row.append(Paragraph("", S["body"]))
            tags.append(row)
            row = []

    if tags:
        tag_grid = Table(tags, colWidths=[CONTENT_W/4-4]*4,
                         hAlign="LEFT")
        tag_grid.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 2),
            ("RIGHTPADDING", (0,0), (-1,-1), 2),
            ("TOPPADDING", (0,0), (-1,-1), 2),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ]))
        inner.append(tag_grid)
        inner.append(Spacer(1, 5))

    # Tips
    inner.append(Paragraph("💡  Study Tips", S["body_bold"]))
    for tip in tips:
        inner.append(Paragraph(f"• {tip}", S["bullet"]))

    if example_code:
        inner.append(Spacer(1, 4))
        inner.append(Paragraph("📝  Quick Example (Python)", S["body_bold"]))
        for line in example_code.strip().split("\n"):
            inner.append(Paragraph(
                line.replace(" ", "&nbsp;"),
                ParagraphStyle("code", fontName="Courier", fontSize=7.5,
                               textColor=colors.HexColor("#1D4ED8"),
                               leading=11, leftIndent=6)))

    # Wrap in card table
    card = Table([[inner]], colWidths=[CONTENT_W])
    lc = color
    card.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ("BOX", (0,0), (-1,-1), 1.5, lc),
        ("LINEBEFORE", (0,0), (0,-1), 4, lc),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return [card, Spacer(1, 5*mm)]

def info_box(text, color, icon="ℹ️"):
    S = make_styles()
    p = Paragraph(f"{icon}  {text}", S["tip"])
    tbl = Table([[p]], colWidths=[CONTENT_W])
    bg = colors.HexColor("#ECFDF5") if color == ACCENT_GREEN else colors.HexColor("#FFF7ED")
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("BOX", (0,0), (-1,-1), 1, color),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    return [tbl, Spacer(1, 4*mm)]

# ── COVER PAGE ────────────────────────────────────────────────────────────────

def build_cover(story, S):
    # Dark background via big table
    cover_content = [
        Spacer(1, 18*mm),
        Paragraph("🚀", ParagraphStyle("emoji", fontName="Helvetica-Bold",
                                        fontSize=42, alignment=TA_CENTER, leading=50)),
        Spacer(1, 4*mm),
        Paragraph("DSA Mastery Roadmap", S["cover_title"]),
        Paragraph("From Zero to FAANG-Ready", S["cover_sub"]),
        Spacer(1, 6*mm),
        DividerLine(CONTENT_W, colors.HexColor("#3B82F6"), 1),
        Spacer(1, 6*mm),
        Paragraph(
            "A complete, beginner-friendly guide for experienced engineers\n"
            "who want to crack product-based & FAANG interviews",
            S["cover_note"]),
        Spacer(1, 10*mm),
    ]

    # Stats row
    stats = [
        ["20\nWeeks", "150+\nProblems", "12\nPhases", "1\nGoal: FAANG"],
    ]
    stat_table = Table(stats, colWidths=[CONTENT_W/4]*4)
    stat_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#1E3A5F")),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.white),
        ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 12),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#3B82F6")),
        ("ROUNDEDCORNERS", [8]),
    ]))
    cover_content.append(stat_table)
    cover_content.append(Spacer(1, 8*mm))
    cover_content.append(
        Paragraph("By Claude · Built for Engineers Who Mean Business", S["cover_note"]))

    cover_tbl = Table([[[c] for c in cover_content][0]],
                      colWidths=[CONTENT_W])
    # We just add items to story directly:
    story.extend(cover_content)
    story.append(PageBreak())

# ── HOW TO USE ────────────────────────────────────────────────────────────────

def build_how_to_use(story, S):
    story.extend(section_header("HOW TO USE THIS ROADMAP", ACCENT_BLUE))

    intro = (
        "You have 5 years of engineering experience — that's a huge advantage. "
        "You already understand how software works in the real world. "
        "What you need is to build a strong, systematic understanding of "
        "Data Structures & Algorithms (DSA) — the language of technical interviews. "
        "This roadmap takes you from the very basics to advanced concepts, "
        "step-by-step, at a pace that builds real intuition — not just memorization."
    )
    story.append(Paragraph(intro, S["intro"]))
    story.append(Spacer(1, 5*mm))

    rules = [
        ["Rule", "What it means"],
        ["One topic at a time", "Master each concept before moving on. Depth > breadth."],
        ["Code every day", "Even 45 minutes of daily practice beats 6-hour weekend binges."],
        ["Solve without looking", "Attempt every problem first. Looking at solutions skips the growth."],
        ["Understand, don't memorize", "Ask 'WHY does this work?' for every algorithm."],
        ["Track your progress", "Keep a list: Solved / Needs Review / Confident."],
        ["Revisit old topics", "Come back to week 1 topics in week 10 — spaced repetition works."],
    ]
    tbl = Table(rules, colWidths=[CONTENT_W*0.35, CONTENT_W*0.65])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT_BLUE),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#EFF6FF")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.HexColor("#EFF6FF"), colors.HexColor("#F8FAFC")]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#BFDBFE")),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 5*mm))

    story.extend(info_box(
        "Recommended: LeetCode (free tier) + NeetCode.io for structured practice. "
        "Use Python — it's clean, readable, and accepted everywhere.",
        ACCENT_GREEN, "✅"))
    story.append(PageBreak())

# ── PHASE DATA ────────────────────────────────────────────────────────────────

PHASES = [
    # (num, title, weeks, color, description, topics, tips, code)
    (1, "Big-O & Complexity Thinking", "Week 1", ACCENT_BLUE,
     "Before writing a single line of DSA code, you must understand HOW we measure "
     "the efficiency of an algorithm. Big-O notation is the ruler every interviewer uses. "
     "Think of it as: if I double the input size, how much slower does my code get? "
     "This is the single most important concept — every phase builds on it.",
     ["Time Complexity", "Space Complexity", "O(1) Constant", "O(n) Linear",
      "O(log n) Log", "O(n²) Quadratic", "Best/Worst/Avg Case", "Drop Constants"],
     [
         "Don't memorize formulas — learn to COUNT operations in your code.",
         "Practice: look at any loop and immediately say its complexity.",
         "Understand why O(n log n) sort beats O(n²) for large inputs.",
         "Resource: Watch 'Big O Notation' by CS Dojo on YouTube (free, 20 min).",
     ],
     """# Count how many times this runs:
def example(arr):            # n = len(arr)
    for i in arr:            # runs n times  → O(n)
        for j in arr:        # runs n times  → O(n)
            print(i, j)      # total: O(n*n) = O(n²)"""),

    (2, "Arrays & Strings", "Weeks 2–3", ACCENT_GREEN,
     "Arrays are the foundation of everything. Almost every DSA problem uses arrays "
     "or strings in some way. Strings are just arrays of characters. "
     "Master the 'Two Pointer' and 'Sliding Window' patterns here — "
     "they appear in 30%+ of all interview questions.",
     ["Array Basics", "String Manipulation", "Two Pointers", "Sliding Window",
      "Prefix Sum", "Kadane's Algo", "Sorting & Searching", "In-place Tricks"],
     [
         "Two Pointer: Use one pointer at start, one at end. Move them toward each other.",
         "Sliding Window: Expand right pointer, shrink left when condition breaks.",
         "Practice: Two Sum, Best Time to Buy/Sell Stock, Longest Substring Without Repeat.",
         "Target: 15–20 problems on LeetCode (Easy to Medium).",
     ],
     """# Two Pointer: Check if string is palindrome
def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True"""),

    (3, "Hashing & Hash Maps", "Week 4", ACCENT_AMBER,
     "A HashMap (Python dict) lets you look up any value in O(1) — instant time. "
     "This is your most powerful tool. When you're stuck on a problem, "
     "ask yourself: 'Can I store something in a dictionary to avoid re-computing it?' "
     "The answer is YES more often than you think.",
     ["Python dict/set", "Frequency Count", "Anagram Check", "Two Sum Pattern",
      "Grouping", "Collision Handling", "Hash Functions", "Set Operations"],
     [
         "HashMap trades memory for speed — a very common interview trade-off.",
         "Frequency map pattern: count occurrences of each element first.",
         "Practice: Valid Anagram, Group Anagrams, Top K Frequent Elements.",
         "Sets are HashMaps without values — use them for 'has this been seen before?'",
     ],
     """# HashMap: Find two numbers that add to target
def two_sum(nums, target):
    seen = {}  # value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i"""),

    (4, "Linked Lists", "Week 5", ACCENT_PURPLE,
     "A linked list is a chain of nodes — each node holds a value and points to the next. "
     "Unlike arrays, there's no index-based access. You must traverse from the head. "
     "Linked list problems train your pointer manipulation skills, "
     "which carry over to trees and graphs.",
     ["Singly Linked", "Doubly Linked", "Reversal", "Fast & Slow Pointers",
      "Cycle Detection", "Merge Lists", "Dummy Node Trick", "Node Deletion"],
     [
         "ALWAYS draw the pointers on paper before coding — prevents bugs.",
         "Fast & Slow pointer (Floyd's): fast moves 2 steps, slow moves 1. Meets at cycle.",
         "Dummy head node trick: simplifies edge cases for head deletion.",
         "Practice: Reverse Linked List, Detect Cycle, Merge Two Sorted Lists.",
     ],
     """# Reverse a linked list — classic interview question
def reverse_list(head):
    prev = None
    curr = head
    while curr:
        next_node = curr.next  # save next
        curr.next = prev       # reverse pointer
        prev = curr            # move prev forward
        curr = next_node       # move curr forward
    return prev  # new head"""),

    (5, "Stacks & Queues", "Week 6", ACCENT_ROSE,
     "Stack = Last In, First Out (like a stack of plates). "
     "Queue = First In, First Out (like a line at a coffee shop). "
     "Stacks are used for undo operations, expression parsing, and DFS. "
     "Queues are used for BFS and task scheduling. Simple but powerful.",
     ["Stack (LIFO)", "Queue (FIFO)", "Monotonic Stack", "Deque",
      "Min Stack", "Valid Parentheses", "BFS with Queue", "Expression Eval"],
     [
         "Python: use a list as a stack (append/pop). Use collections.deque as a queue.",
         "Monotonic Stack: elements stay in sorted order — great for 'next greater element'.",
         "Parentheses matching is THE classic stack problem. Understand it deeply.",
         "Practice: Valid Parentheses, Daily Temperatures, Min Stack.",
     ],
     """# Stack: Check if brackets are balanced
def is_valid(s):
    stack = []
    pairs = {')': '(', '}': '{', ']': '['}
    for ch in s:
        if ch in '({[':
            stack.append(ch)
        elif stack and stack[-1] == pairs[ch]:
            stack.pop()
        else:
            return False
    return len(stack) == 0"""),

    (6, "Recursion & Backtracking", "Weeks 7–8", ACCENT_BLUE,
     "Recursion is when a function calls itself to solve a smaller version of the problem. "
     "It's mind-bending at first — but once it clicks, it unlocks trees, graphs, and DP. "
     "Backtracking is recursion with a 'try and undo' pattern: explore all possibilities, "
     "then backtrack when a path doesn't work.",
     ["Base Case", "Recursive Case", "Call Stack", "Memoization Intro",
      "Subsets", "Permutations", "Combinations", "N-Queens", "Sudoku"],
     [
         "Always define: (1) Base case — when to stop. (2) Recursive case — smaller problem.",
         "Trace through small examples by hand. Trust the recursion.",
         "Backtracking template: choose → explore → un-choose.",
         "Practice: Fibonacci, Subsets, Permutations, Combination Sum.",
     ],
     """# Backtracking: Generate all subsets
def subsets(nums):
    result = []
    def backtrack(start, current):
        result.append(current[:])  # add copy
        for i in range(start, len(nums)):
            current.append(nums[i])    # choose
            backtrack(i + 1, current)  # explore
            current.pop()              # un-choose
    backtrack(0, [])
    return result"""),

    (7, "Binary Search", "Week 9", ACCENT_GREEN,
     "Binary search cuts the problem in half every step — making O(n) into O(log n). "
     "It's not just for sorted arrays. The real skill is recognizing WHEN to apply it. "
     "Any time you're searching for a minimum/maximum value that satisfies some condition, "
     "binary search is your tool.",
     ["Classic Binary Search", "Search on Answer", "Left/Right Boundary",
      "Rotated Array", "Matrix Search", "Peak Element", "Sqrt(x)", "Guess Number"],
     [
         "Template: low=0, high=len-1, mid=(low+high)//2, adjust based on condition.",
         "Off-by-one errors are common — always test with arrays of size 1, 2, 3.",
         "'Search on Answer' pattern: binary search on the ANSWER RANGE not the array.",
         "Practice: Binary Search, Find Min in Rotated Array, Koko Eating Bananas.",
     ],
     """# Binary Search template — memorize this
def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1   # target is in right half
        else:
            high = mid - 1  # target is in left half
    return -1  # not found"""),

    (8, "Trees — Binary Trees & BST", "Weeks 10–11", ACCENT_PURPLE,
     "Trees are everywhere in CS — file systems, databases, DOM, org charts. "
     "A binary tree has at most 2 children per node. "
     "A Binary Search Tree (BST) is ordered: left < root < right. "
     "Master the 3 traversals (Inorder, Preorder, Postorder) — they're the building blocks "
     "for almost every tree problem.",
     ["Tree Nodes", "DFS Traversals", "BFS / Level Order", "BST Search/Insert",
      "Tree Height", "Lowest Common Ancestor", "Balanced Tree", "Serialize/Deserialize"],
     [
         "DFS uses recursion (or stack). BFS uses a queue.",
         "Inorder of a BST gives sorted output — very useful property.",
         "Most tree problems follow: process current node, recurse left, recurse right.",
         "Practice: Invert Binary Tree, Max Depth, Level Order, Validate BST.",
     ],
     """# DFS: Max depth of binary tree
def max_depth(root):
    if not root:       # base case: empty tree
        return 0
    left  = max_depth(root.left)   # depth of left subtree
    right = max_depth(root.right)  # depth of right subtree
    return 1 + max(left, right)    # +1 for current node"""),

    (9, "Heaps & Priority Queues", "Week 12", ACCENT_AMBER,
     "A Heap is a special tree that always keeps the min (or max) element at the top. "
     "This gives you O(1) access to the minimum/maximum and O(log n) insert/delete. "
     "Heaps are the secret weapon for 'Top K' and 'K-th Largest' type problems.",
     ["Min Heap", "Max Heap", "heapq module", "Top K Elements",
      "K-th Largest", "Merge K Lists", "Task Scheduler", "Median Finder"],
     [
         "Python's heapq is a MIN heap. For MAX heap: push negative values.",
         "When you see 'K largest' / 'K most frequent' — think heap.",
         "Heap insert/delete: O(log n). Peek min: O(1).",
         "Practice: Kth Largest Element, Top K Frequent, Find Median from Data Stream.",
     ],
     """# heapq: Find K largest elements
import heapq
def k_largest(nums, k):
    # Use min-heap of size k
    heap = nums[:k]
    heapq.heapify(heap)           # O(k)
    for num in nums[k:]:
        if num > heap[0]:         # larger than smallest in heap
            heapq.heapreplace(heap, num)
    return sorted(heap, reverse=True)"""),

    (10, "Graphs", "Weeks 13–14", ACCENT_ROSE,
     "A graph is a set of nodes connected by edges. Social networks, maps, dependencies — "
     "all graphs. Trees are actually a special case of graphs (connected, no cycles). "
     "The two key traversals — DFS and BFS — apply here just like in trees, "
     "but you now need to track 'visited' nodes to avoid infinite loops.",
     ["Adjacency List/Matrix", "DFS", "BFS", "Cycle Detection",
      "Topological Sort", "Union Find", "Shortest Path", "Connected Components",
      "Islands Pattern", "Dijkstra's Algo"],
     [
         "Always build the graph first (adjacency list = dict of lists in Python).",
         "BFS → shortest path in unweighted graph. Dijkstra → shortest path weighted.",
         "Topological sort → dependency ordering (build systems, course schedules).",
         "Practice: Number of Islands, Clone Graph, Course Schedule, Pacific Atlantic.",
     ],
     """# BFS: Shortest path in unweighted graph
from collections import deque
def bfs(graph, start, end):
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        node, path = queue.popleft()
        if node == end:
            return path
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    return []"""),

    (11, "Dynamic Programming (DP)", "Weeks 15–17", ACCENT_PURPLE,
     "DP is about solving complex problems by breaking them into overlapping subproblems "
     "and remembering (memoizing) results. It's the hardest topic — and the most rewarding. "
     "The key insight: every DP problem is just recursion + caching. "
     "Start with recursion first, then add memoization, then convert to bottom-up.",
     ["Memoization (Top-Down)", "Tabulation (Bottom-Up)", "1D DP", "2D DP",
      "Fibonacci Pattern", "0/1 Knapsack", "Coin Change", "Longest Subsequence",
      "Edit Distance", "DP on Strings"],
     [
         "ALWAYS start by writing the brute-force recursive solution first.",
         "Memoization = recursion + dictionary cache. Start here before bottom-up.",
         "Identify: What is the 'state'? What is the 'recurrence relation'?",
         "Practice: Climbing Stairs, Coin Change, Longest Common Subsequence, House Robber.",
     ],
     """# Coin Change — classic DP (bottom-up)
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0  # base case: 0 coins for amount 0
    for a in range(1, amount + 1):
        for coin in coins:
            if coin <= a:
                dp[a] = min(dp[a], 1 + dp[a - coin])
    return dp[amount] if dp[amount] != float('inf') else -1"""),

    (12, "Greedy, Tries & Advanced", "Weeks 18–20", ACCENT_AMBER,
     "Greedy algorithms make the locally optimal choice at each step, hoping to find the "
     "global optimum. Tries (prefix trees) are specialized for string search problems. "
     "This phase rounds out your toolkit with the remaining patterns "
     "that appear in hard-level interviews.",
     ["Greedy Patterns", "Interval Scheduling", "Trie / Prefix Tree",
      "Segment Tree (intro)", "Bit Manipulation", "Math Tricks",
      "Two-Pass Tricks", "Monotonic Deque"],
     [
         "Greedy works when: local optimal = global optimal. Prove it before trusting it.",
         "Interval problems: sort by start or end time, then sweep.",
         "Trie: great for autocomplete, word search, prefix matching.",
         "Practice: Jump Game, Merge Intervals, Implement Trie, Word Search II.",
     ]),
]

# ── WEEKLY SCHEDULE TABLE ─────────────────────────────────────────────────────

def build_schedule(story, S):
    story.extend(section_header("WEEK-BY-WEEK SCHEDULE", ACCENT_GREEN))

    rows = [["Week", "Topic / Phase", "Key Problems to Solve", "Goal"]]
    schedule = [
        ("1",    "Big-O Complexity",       "Practice counting loops mentally",          "Think in time/space"),
        ("2–3",  "Arrays & Strings",       "Two Sum, Best Buy/Sell Stock, Longest Substr","2 pointer + sliding window"),
        ("4",    "Hash Maps & Sets",       "Valid Anagram, Group Anagrams, Top K Freq", "O(1) lookup reflex"),
        ("5",    "Linked Lists",           "Reverse List, Detect Cycle, Merge Lists",   "Pointer confidence"),
        ("6",    "Stacks & Queues",        "Valid Parens, Daily Temps, Min Stack",      "LIFO/FIFO mastery"),
        ("7–8",  "Recursion & Backtrack",  "Subsets, Permutations, Combination Sum",   "Recursive thinking"),
        ("9",    "Binary Search",          "Binary Search, Rotated Array, Koko Banana", "Log n intuition"),
        ("10–11","Trees & BST",            "Invert Tree, Max Depth, Validate BST",     "DFS/BFS on trees"),
        ("12",   "Heaps & Priority Q",    "Top K Freq, Kth Largest, Merge K Lists",   "Heap when to use"),
        ("13–14","Graphs",                 "Islands, Clone Graph, Course Schedule",    "Graph traversal"),
        ("15–17","Dynamic Programming",   "Climbing Stairs, Coin Change, LCS, Robber","DP state design"),
        ("18–20","Greedy, Trie, Mock",    "Jump Game, Merge Intervals, Mock Interviews","Interview-ready"),
    ]
    rows.extend(schedule)

    col_widths = [CONTENT_W*0.1, CONTENT_W*0.22, CONTENT_W*0.42, CONTENT_W*0.26]
    tbl = Table(rows, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), DARK_BG),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.HexColor("#F8FAFC"), colors.HexColor("#EFF6FF")]),
        ("TEXTCOLOR", (0,1), (-1,-1), TEXT_DARK),
        ("TEXTCOLOR", (3,1), (3,-1), ACCENT_GREEN),
        ("FONTNAME", (3,1), (3,-1), "Helvetica-Oblique"),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 5*mm))
    story.append(PageBreak())

# ── PATTERNS CHEAT SHEET ──────────────────────────────────────────────────────

def build_patterns(story, S):
    story.extend(section_header("INTERVIEW PATTERNS CHEAT SHEET", ACCENT_AMBER))

    story.append(Paragraph(
        "When you see this clue in a problem → use this pattern:",
        S["body_bold"]))
    story.append(Spacer(1, 3*mm))

    patterns = [
        ["Clue in Problem", "Pattern to Use", "Example Problems"],
        ["'Sorted array', find target", "Binary Search", "Search in Rotated Array"],
        ["'K largest / K smallest'", "Heap (Priority Queue)", "Top K Frequent Elements"],
        ["'All subsets / combinations'", "Backtracking", "Subsets, Combination Sum"],
        ["'Shortest path' (unweighted)", "BFS", "Word Ladder, 0-1 Matrix"],
        ["'Shortest path' (weighted)", "Dijkstra's BFS + Heap", "Network Delay Time"],
        ["'Count / find duplicates'", "HashMap / HashSet", "Contains Duplicate, Two Sum"],
        ["'Contiguous subarray'", "Sliding Window", "Max Sum Subarray, Fruits Into Baskets"],
        ["'Overlapping subproblems'", "Dynamic Programming", "Coin Change, LCS"],
        ["'Pair that sums to X'", "Two Pointers", "Two Sum II, 3Sum"],
        ["'Balanced parentheses'", "Stack", "Valid Parentheses, Generate Parens"],
        ["'Order / rank / schedule'", "Topological Sort", "Course Schedule, Alien Dictionary"],
        ["'Interval overlap'", "Sort + Sweep", "Merge Intervals, Meeting Rooms"],
        ["'Prefix / word search'", "Trie", "Implement Trie, Word Search II"],
        ["'Connected components'", "Union Find / DFS", "Number of Islands, Accounts Merge"],
    ]

    col_widths = [CONTENT_W*0.38, CONTENT_W*0.3, CONTENT_W*0.32]
    tbl = Table(patterns, colWidths=col_widths)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT_AMBER),
        ("TEXTCOLOR", (0,0), (-1,0), TEXT_DARK),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTNAME", (1,1), (1,-1), "Helvetica-Bold"),
        ("TEXTCOLOR", (1,1), (1,-1), ACCENT_BLUE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.HexColor("#FFFBEB"), colors.HexColor("#F8FAFC")]),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#FDE68A")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 5*mm))
    story.append(PageBreak())

# ── INTERVIEW PREP ────────────────────────────────────────────────────────────

def build_interview_prep(story, S):
    story.extend(section_header("INTERVIEW DAY STRATEGY", ACCENT_ROSE))

    steps = [
        ("1. Understand First (2–3 min)",
         "Read the problem twice. Ask clarifying questions: What's the input size? "
         "Can values be negative? Can the array be empty? What should I return?"),
        ("2. Think Out Loud — Always",
         "Interviewers hire people they can work WITH. Talk through your thought process. "
         "A wrong answer explained clearly beats a silent correct answer."),
        ("3. Brute Force → Optimize",
         "State the naive O(n²) or O(n³) solution first. Then say: "
         "'Can I do better?' Then optimize step by step."),
        ("4. Write Clean Code",
         "Use meaningful variable names. Write helper functions. "
         "Avoid magic numbers. Clean code signals a professional engineer."),
        ("5. Test Your Code",
         "Walk through your code with the example. Then test with edge cases: "
         "empty input, single element, all same values, negative numbers."),
        ("6. Analyze Complexity",
         "Always state time and space complexity at the end. "
         "Interviewers will ask — be ready with the answer."),
    ]

    for title, body in steps:
        data = [[Paragraph(title, S["body_bold"]),
                 Paragraph(body, S["body"])]]
        tbl = Table(data, colWidths=[CONTENT_W*0.32, CONTENT_W*0.68])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), colors.HexColor("#FFF1F2")),
            ("BACKGROUND", (1,0), (1,0), colors.HexColor("#F8FAFC")),
            ("TEXTCOLOR", (0,0), (0,0), ACCENT_ROSE),
            ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#FECDD3")),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("RIGHTPADDING", (0,0), (-1,-1), 10),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 2*mm))

    story.append(Spacer(1, 4*mm))
    story.extend(section_header("RESOURCES & FINAL TIPS", ACCENT_PURPLE))

    resources = [
        ["Resource", "What For", "Cost"],
        ["LeetCode", "Problem practice — essential", "Free (paid optional)"],
        ["NeetCode.io", "Curated 150 problems with roadmap", "Free"],
        ["NeetCode YouTube", "Video explanations of hard problems", "Free"],
        ["Grokking the Coding Interview", "Pattern-based learning", "Paid (worth it)"],
        ["CTCI (Cracking the Coding Interview)", "Classic interview prep book", "Book ~$30"],
        ["CS Dojo YouTube", "Big-O, Python fundamentals", "Free"],
        ["AlgoExpert", "Structured video solutions", "Paid"],
    ]

    col_widths = [CONTENT_W*0.3, CONTENT_W*0.45, CONTENT_W*0.25]
    r_tbl = Table(resources, colWidths=col_widths)
    r_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), ACCENT_PURPLE),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTNAME", (0,1), (0,-1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [colors.HexColor("#F5F3FF"), colors.HexColor("#F8FAFC")]),
        ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#DDD6FE")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TEXTCOLOR", (2,1), (2,-1), ACCENT_GREEN),
        ("FONTNAME", (2,1), (2,-1), "Helvetica-Oblique"),
    ]))
    story.append(r_tbl)
    story.append(Spacer(1, 6*mm))

    story.extend(info_box(
        "Final reminder: You already have 5 years of engineering experience. "
        "Use that! Connect every DSA concept to real systems you've built. "
        "That context makes your answers richer and more memorable to interviewers. "
        "Consistency beats intensity — 45 min daily for 20 weeks will get you there.",
        ACCENT_GREEN, "🎯"))

# ── PAGE TEMPLATE (header/footer) ─────────────────────────────────────────────

def on_page(canvas, doc):
    W_pg, H_pg = A4
    canvas.saveState()
    # Top bar
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, H_pg - 22, W_pg, 22, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(15*mm, H_pg - 14, "DSA MASTERY ROADMAP — FAANG Edition")
    canvas.setFont("Helvetica", 7)
    canvas.drawRightString(W_pg - 15*mm, H_pg - 14, f"Page {doc.page}")
    # Bottom line
    canvas.setStrokeColor(ACCENT_BLUE)
    canvas.setLineWidth(1)
    canvas.line(15*mm, 12*mm, W_pg - 15*mm, 12*mm)
    canvas.setFillColor(TEXT_MUTED)
    canvas.setFont("Helvetica", 6.5)
    canvas.drawCentredString(W_pg/2, 7*mm,
        "Practice consistently · Build intuition · Get that offer")
    canvas.restoreState()

def on_first_page(canvas, doc):
    W_pg, H_pg = A4
    canvas.saveState()
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, W_pg, H_pg, fill=1, stroke=0)
    canvas.restoreState()

# ── MAIN BUILD ────────────────────────────────────────────────────────────────

def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=28*mm, bottomMargin=18*mm,
        title="DSA Mastery Roadmap",
        author="Claude"
    )
    S  = make_styles()
    story = []

    # ── Cover (page 1 — full dark background) ──
    doc_first = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )
    build_cover(story, S)

    # ── How to Use ──
    build_how_to_use(story, S)

    # ── All Phases ──
    story.extend(section_header("THE 12-PHASE LEARNING PATH", ACCENT_PURPLE))
    story.extend(info_box(
        "Each phase builds on the previous one. Don't skip ahead. "
        "If a phase feels hard, slow down — that's where the growth is.",
        ACCENT_AMBER, "⚠️"))

    for phase_data in PHASES:
        story.extend(phase_card(*phase_data))

    story.append(PageBreak())

    # ── Weekly Schedule ──
    build_schedule(story, S)

    # ── Patterns ──
    build_patterns(story, S)

    # ── Interview Prep ──
    build_interview_prep(story, S)

    doc.build(story,
              onFirstPage=on_first_page,
              onLaterPages=on_page)
    print("PDF built successfully:", output_path)

if __name__ == "__main__":
    build_pdf("/mnt/user-data/outputs/DSA_Mastery_Roadmap.pdf")

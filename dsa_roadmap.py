import sys
sys.path.insert(0, '/home/claude')
from pdf_utils import *

OUT = '/mnt/user-data/outputs/01_DSA_Mastery_Roadmap.pdf'
ACCENT = C_PRIMARY
TITLE = 'DSA Mastery Roadmap — FAANG Interview Preparation'

def p(text, style): return Paragraph(text, style)
def sp(n=4): return Spacer(1, n)

def make_story():
    S = make_styles(ACCENT)
    story = []

    # ── COVER PAGE ──────────────────────────────────────────────────
    story += [sp(60),
        p('DSA MASTERY ROADMAP', S['cover_title']),
        p('Data Structures &amp; Algorithms', S['cover_sub']),
        sp(8),
        p('FAANG-Level Interview Preparation · 4-Week Intensive Program', S['cover_tag']),
        sp(6),
        p('Google · Meta · Amazon · Apple · Netflix · OpenAI · Anthropic · Microsoft · Nvidia · Stripe · Databricks', S['muted']),
        sp(40), hr(ACCENT, 2),
        p('Senior Software Engineer &amp; AI Engineer Readiness', S['cover_sub']),
        p('4–6 Hours Daily · Beginner to Advanced · Blind 75 + NeetCode 150 + FAANG Patterns', S['muted']),
        PageBreak()]

    # ── TABLE OF CONTENTS ───────────────────────────────────────────
    story += [p('TABLE OF CONTENTS', S['h1']), hr(ACCENT), sp(4)]
    toc = [
        ('MASTER STRATEGY', 'Problem-solving frameworks, thinking models, communication'),
        ('WEEK 1', 'Arrays, Strings, Hashing, Two Pointers, Sliding Window, Binary Search'),
        ('WEEK 2', 'Linked Lists, Stacks, Queues, Trees, BST, Heaps, Tries'),
        ('WEEK 3', 'Graphs, DFS/BFS, Union-Find, Dynamic Programming, Greedy'),
        ('WEEK 4', 'Backtracking, Segment Trees, Monotonic Stack, Hard Problems, Mocks'),
        ('FAANG PATTERNS', 'Top 20 recurring interview patterns with templates'),
        ('BLIND 75 + NEETCODE', 'Curated problem sets with priority labels'),
        ('RESOURCES', 'Books, channels, repos, LeetCode lists'),
        ('CHEAT SHEET', 'Big-O, interview-day strategies, revision checklist'),
    ]
    for title, desc in toc:
        story.append(p(f'<b><font color="#1F6FEB">{title}</font></b>  —  {desc}', S['toc']))
    story.append(PageBreak())

    # ── MASTER STRATEGY ─────────────────────────────────────────────
    story += [p('MASTER STRATEGY & MENTAL MODELS', S['h1']), hr(ACCENT)]

    story += [p('Interview Thinking Framework', S['h2']),
        p('Every FAANG coding interview follows a predictable structure. Master this 5-step framework and you will outperform 90% of candidates:', S['body']),
        p('<b>STEP 1 — UNDERSTAND (3–4 min):</b> Restate the problem in your own words. Identify inputs, outputs, constraints, edge cases. Never start coding without this.', S['bullet']),
        p('<b>STEP 2 — EXAMPLES (2 min):</b> Walk through 2–3 concrete examples. Include edge cases: empty input, single element, all-same values, negatives.', S['bullet']),
        p('<b>STEP 3 — APPROACH (3–5 min):</b> Think aloud about brute force first, then optimize. Discuss Big-O. Name the pattern you recognize (sliding window, BFS, DP…).', S['bullet']),
        p('<b>STEP 4 — CODE (15–20 min):</b> Write clean, readable code. Narrate each section. Use meaningful variable names. Prefer clarity over cleverness.', S['bullet']),
        p('<b>STEP 5 — VERIFY (3–5 min):</b> Dry-run with your test cases. Check edge cases. State final time/space complexity. Offer optimizations if time allows.', S['bullet']),
        sp(4)]

    story += [p('Big-O Analysis — Quick Reference', S['h2'])]
    bigo_data = [
        ['Complexity', 'Name', 'Example', 'Max N (1 sec)'],
        ['O(1)', 'Constant', 'HashMap lookup', 'Any'],
        ['O(log N)', 'Logarithmic', 'Binary Search', '10^18'],
        ['O(N)', 'Linear', 'Single loop', '10^8'],
        ['O(N log N)', 'Linearithmic', 'Merge Sort', '10^6'],
        ['O(N^2)', 'Quadratic', 'Nested loops', '10^4'],
        ['O(N^3)', 'Cubic', 'Triple nested', '500'],
        ['O(2^N)', 'Exponential', 'Subsets/backtrack', '20–25'],
        ['O(N!)', 'Factorial', 'Permutations', '10–12'],
    ]
    story.append(Table(bigo_data, colWidths=[70, 90, 130, 90],
        style=dark_table_style(ACCENT)))
    story.append(sp(6))

    story += [p('Dry-Run Methodology', S['h2']),
        p('Dry-running (tracing code on paper/whiteboard) is non-negotiable in FAANG interviews. Follow this pattern:', S['body']),
        p('1. Create a variable-tracking table: columns = each variable, rows = each iteration.', S['bullet']),
        p('2. For arrays/trees: draw the data structure and annotate pointers at each step.', S['bullet']),
        p('3. For recursion: draw the call stack explicitly showing parameters and return values.', S['bullet']),
        p('4. For graphs: mark visited nodes and show the queue/stack state at each BFS/DFS step.', S['bullet']),
        p('5. Validate at least the happy path + 1 edge case before declaring correctness.', S['bullet']),
        sp(4)]

    story += [p('Space-Time Tradeoff Analysis', S['h2']),
        p('At FAANG, you must proactively discuss tradeoffs. Structure it as:', S['body']),
        p('<b>Current approach:</b> O(N^2) time, O(1) space — brute force with nested loops.', S['bullet']),
        p('<b>Optimization 1:</b> Use a HashMap → O(N) time, O(N) space. Trading space for time.', S['bullet']),
        p('<b>Optimization 2:</b> Two-pointer (if sorted) → O(N log N) time (sort), O(1) space.', S['bullet']),
        p('<b>When to choose:</b> If memory is constrained, prefer sorted+two-pointer. If speed is critical and memory is cheap, use HashMap.', S['bullet']),
        sp(4), PageBreak()]

    # ── WEEK 1 ──────────────────────────────────────────────────────
    story += [p('WEEK 1 — FOUNDATIONS', S['h1']), hr(ACCENT),
        p('Focus: Arrays · Strings · Hashing · Two Pointers · Sliding Window · Binary Search', S['cover_tag']),
        p('Goal: Build rock-solid fundamentals. Be able to solve Easy/Medium problems under time pressure.', S['body']), sp(4)]

    # Day-by-day week 1
    days_w1 = [
        ('DAY 1', 'Arrays & Hashing', [
            'Core: Array indexing, slicing, in-place mutation, prefix sums, difference arrays.',
            'HashMap fundamentals: O(1) lookup, collision handling, Python dict internals.',
            'Pattern: Two-Sum family — recognize anytime you need pair/complement lookup.',
            'Concepts: Frequency maps, counting, grouping by key.',
            'Problems: Two Sum (LC 1), Contains Duplicate (LC 217), Valid Anagram (LC 242), Group Anagrams (LC 49), Top K Frequent Elements (LC 347).',
            'Practice goal: Solve 5 problems. All in under 15 min each.',
            'Insight: HashMap problems are 30%+ of FAANG Easy rounds. Never overlook them.',
        ], '3–4 hrs'),
        ('DAY 2', 'Two Pointers', [
            'Core: Left/right pointers on sorted arrays. Fast/slow pointers for cycles.',
            'Pattern recognition: "Find pair with target sum in sorted array" → Two Pointers.',
            'Pattern: Merge two sorted arrays, remove duplicates, container with most water.',
            'Problems: Valid Palindrome (LC 125), 3Sum (LC 15), Container With Most Water (LC 11), Trapping Rain Water (LC 42), Move Zeroes (LC 283).',
            'Edge cases: Duplicates in 3Sum (skip duplicates after sorting). Pointer crossing condition.',
            'Practice goal: 5 problems. Understand why sorting enables two pointers.',
            'Insight: Two Pointers eliminates one loop → O(N) from O(N^2). Always ask: "Is the array sorted or can I sort it?"',
        ], '3–4 hrs'),
        ('DAY 3', 'Sliding Window', [
            'Core: Fixed-size window vs variable-size window. When to expand/shrink.',
            'Template: left=0, right=0, while right < n: expand; while condition violated: shrink left.',
            'Pattern: Substring with constraint, max/min subarray with property.',
            'Problems: Best Time to Buy/Sell Stock (LC 121), Longest Substring Without Repeating (LC 3), Longest Repeating Char Replacement (LC 424), Permutation in String (LC 567), Minimum Window Substring (LC 76).',
            'Advanced: Two-pointer + HashMap for character frequency tracking.',
            'Practice goal: 5 problems. Code the template from memory.',
            'Insight: Sliding window reduces O(N^2) nested loop to O(N). Trigger: "subarray/substring" + "max/min length".',
        ], '3–4 hrs'),
        ('DAY 4', 'Binary Search', [
            'Core: Sorted search space. Left/right boundary patterns. Template variants.',
            'Templates: (1) Classic exact search (2) Leftmost valid (3) Rightmost valid (4) Answer-space binary search.',
            'Answer-space pattern: Binary search on the ANSWER when "can we achieve X?" is monotone.',
            'Problems: Binary Search (LC 704), Search 2D Matrix (LC 74), Koko Eating Bananas (LC 875), Find Min in Rotated Array (LC 153), Search Rotated Array (LC 33), Median of Two Sorted Arrays (LC 4).',
            'Common mistakes: Off-by-one errors in mid calculation. Use mid = left + (right-left)//2.',
            'Practice goal: 6 problems. Write all 3 templates from memory.',
            'Insight: Binary search on answer is a meta-pattern used in many Hard problems. If the problem asks for "minimum maximum" or "maximum minimum", think binary search on answer.',
        ], '4 hrs'),
        ('DAY 5', 'Strings Deep Dive', [
            'Core: String immutability in Python. StringIO for O(1) appends. String hashing.',
            'Patterns: Palindrome checks, anagram detection, pattern matching, encoding/decoding.',
            'Rolling hash: Rabin-Karp algorithm for O(N) substring search.',
            'Problems: Encode/Decode Strings (LC 271), Longest Palindromic Substring (LC 5), Palindromic Substrings (LC 647), Zigzag (LC 6), Reverse Words (LC 151).',
            'Python-specific: ord(), chr(), str.translate(), collections.Counter for anagrams.',
            'Practice goal: 5 problems. Implement Rabin-Karp.',
            'Insight: String problems at FAANG often hide array/hashing patterns. Always convert to frequency map or index first.',
        ], '3–4 hrs'),
        ('DAY 6', 'Prefix Sums & Advanced Arrays', [
            'Core: Prefix sum array for O(1) range sum queries. 2D prefix sums.',
            'Difference array: Range update in O(1), query in O(N). Used in interval problems.',
            'Pattern: Subarray sum = target → prefix sum + HashMap (LC 560 pattern).',
            'Problems: Subarray Sum Equals K (LC 560), Product of Array Except Self (LC 238), Maximum Product Subarray (LC 152), Range Sum Query (LC 303), 2D Range Sum (LC 304).',
            'Practice goal: 5 problems. Implement 2D prefix sum.',
            'Insight: Prefix sum + HashMap is one of the most powerful O(N) techniques. Learn it deeply.',
        ], '3–4 hrs'),
        ('DAY 7', 'Week 1 Review & Mock', [
            'Morning: Re-solve 3 problems you struggled with this week without looking at solutions.',
            'Afternoon: Timed mock — 2 LeetCode Medium problems in 45 minutes each.',
            'Review: Big-O of all techniques covered. Whiteboard communication practice.',
            'Checklist: Can you code Two Sum, Sliding Window template, Binary Search from memory?',
            'Weekly assessment: 25+ problems solved, 80%+ accuracy on Mediums.',
            'Weak areas: Identify and note 2 patterns to revisit in Week 4.',
        ], '4–5 hrs'),
    ]

    for day, topic, points, hrs in days_w1:
        story += [p(f'{day} — {topic}', S['h3']),
            p(f'<b>Estimated Time:</b> {hrs}', S['muted'])]
        for pt in points:
            story.append(p(f'• {pt}', S['bullet']))
        story.append(sp(3))

    story.append(PageBreak())

    # ── WEEK 2 ──────────────────────────────────────────────────────
    story += [p('WEEK 2 — DATA STRUCTURES', S['h1']), hr(ACCENT),
        p('Focus: Linked Lists · Stacks · Queues · Trees · BST · Heaps · Tries', S['cover_tag']),
        p('Goal: Fluency with pointer-based structures and hierarchical data. Medium problems in under 20 min.', S['body']), sp(4)]

    days_w2 = [
        ('DAY 8', 'Linked Lists', [
            'Core: Singly vs doubly. Node class. Pointer manipulation without losing references.',
            'Patterns: Reversal (iterative + recursive), cycle detection (Floyd\'s), merge, nth from end.',
            'Floyd\'s Algorithm: Slow/fast pointers. Meeting point formula for cycle start.',
            'Problems: Reverse LL (LC 206), Merge Two Sorted (LC 21), Reorder List (LC 143), Remove Nth From End (LC 19), LRU Cache (LC 146), Merge K Sorted Lists (LC 23).',
            'Common mistake: Losing next pointer before reassignment. Always save next = curr.next first.',
            'Practice goal: 6 problems. Implement LRU Cache from scratch using OrderedDict.',
        ], '4 hrs'),
        ('DAY 9', 'Stacks & Queues', [
            'Core: Stack LIFO, Queue FIFO. Deque for O(1) both ends. Monotonic patterns.',
            'Monotonic stack: Maintain increasing/decreasing invariant. Pattern: "next greater/smaller element".',
            'Monotonic queue: Sliding window maximum/minimum in O(N).',
            'Problems: Valid Parentheses (LC 20), Min Stack (LC 155), Evaluate RPN (LC 150), Daily Temperatures (LC 739), Largest Rectangle in Histogram (LC 84), Sliding Window Maximum (LC 239).',
            'Insight: Monotonic stack/queue are hidden in 20%+ of Hard problems. Master them in Week 2.',
            'Practice goal: 6 problems. Code monotonic stack template from memory.',
        ], '4 hrs'),
        ('DAY 10', 'Binary Trees — DFS', [
            'Core: Tree node class. Height, depth, diameter. DFS patterns: pre/in/post order.',
            'Recursive DFS template: base case (null check) + left subtree + right subtree + return value.',
            'Common patterns: Max/min path sum, diameter, balanced check, LCA.',
            'Problems: Invert Binary Tree (LC 226), Max Depth (LC 104), Diameter (LC 543), Balanced Tree (LC 110), Same Tree (LC 100), Path Sum II (LC 113), Max Path Sum (LC 124).',
            'Serialization: DFS with None markers for null nodes. Used in interviews for tree marshalling.',
            'Practice goal: 7 problems. Code all 3 DFS traversal orders from memory.',
        ], '4 hrs'),
        ('DAY 11', 'Binary Trees — BFS & BST', [
            'Core: Level-order traversal with deque. BFS gives natural level information.',
            'BST property: left < root < right. In-order traversal of BST gives sorted array.',
            'BST operations: Insert, search, delete (successor/predecessor for deletion).',
            'Problems: Level Order Traversal (LC 102), Right Side View (LC 199), Average of Levels (LC 637), Validate BST (LC 98), Kth Smallest in BST (LC 230), BST Iterator (LC 173), Construct from Preorder+Inorder (LC 105).',
            'Practice goal: 7 problems. Implement BST insert/delete/search from scratch.',
        ], '4 hrs'),
        ('DAY 12', 'Heaps & Priority Queues', [
            'Core: Min-heap, max-heap. Python heapq (min-heap only — negate for max-heap).',
            'Patterns: Top K elements, K-th largest, merge K sorted, median from stream.',
            'Two-heap pattern: Lower-half max-heap + upper-half min-heap for median maintenance.',
            'Problems: Kth Largest (LC 215), Top K Frequent (LC 347), K Closest Points (LC 973), Find Median from Stream (LC 295), Task Scheduler (LC 621), Merge K Sorted Lists (LC 23 — heap variant).',
            'Python: heapq.heappush, heapq.heappop, heapq.nlargest, heapq.nsmallest.',
            'Practice goal: 6 problems. Implement two-heap median tracker from scratch.',
        ], '4 hrs'),
        ('DAY 13', 'Tries', [
            'Core: Prefix tree. TrieNode class with children dict and is_end flag.',
            'Operations: Insert O(L), Search O(L), StartsWith O(L) where L = word length.',
            'Advanced: Word search with DFS on Trie. Wildcard search with BFS.',
            'Problems: Implement Trie (LC 208), Add and Search Word (LC 211), Word Search II (LC 212), Replace Words (LC 648), Maximum XOR of Two Numbers (LC 421 — binary trie).',
            'Insight: Tries appear in 10–15% of Meta/Google interviews. Binary Trie for XOR problems is an advanced pattern.',
            'Practice goal: 5 problems. Implement complete Trie class from memory.',
        ], '3–4 hrs'),
        ('DAY 14', 'Week 2 Review & Mock', [
            'Morning: Code Linked List, Stack, Heap, Trie from memory (no IDE).',
            'Afternoon: 2 timed Mediums — one Tree, one Heap problem. 45 min each.',
            'Evening: Study your Week 2 weakest pattern. Re-solve 2 problems.',
            'Milestone: 45+ total problems solved. Trees and LinkedLists at 85%+ accuracy.',
            'Checklist: All data structure implementations from memory. BFS/DFS templates.',
        ], '4–5 hrs'),
    ]

    for day, topic, points, hrs in days_w2:
        story += [p(f'{day} — {topic}', S['h3']),
            p(f'<b>Estimated Time:</b> {hrs}', S['muted'])]
        for pt in points:
            story.append(p(f'• {pt}', S['bullet']))
        story.append(sp(3))

    story.append(PageBreak())

    # ── WEEK 3 ──────────────────────────────────────────────────────
    story += [p('WEEK 3 — GRAPHS & DYNAMIC PROGRAMMING', S['h1']), hr(ACCENT),
        p('Focus: Graphs · DFS/BFS · Union-Find · Dynamic Programming · Greedy', S['cover_tag']),
        p('Goal: Master the two most interview-heavy advanced topics. Solve Mediums in 20 min, tackle Hards.', S['body']), sp(4)]

    days_w3 = [
        ('DAY 15', 'Graph Fundamentals & BFS', [
            'Core: Adjacency list vs matrix. Directed vs undirected. Weighted vs unweighted.',
            'BFS template: deque, visited set, level tracking. Use for shortest path in unweighted graphs.',
            'Problems: Number of Islands (LC 200), Clone Graph (LC 133), Rotting Oranges (LC 994), Walls and Gates (LC 286), Shortest Path in Binary Matrix (LC 1091).',
            'Multi-source BFS: Start BFS from multiple sources simultaneously (Rotting Oranges pattern).',
            'Practice goal: 5 problems. Code BFS template for graphs from memory.',
        ], '4 hrs'),
        ('DAY 16', 'Graph DFS & Cycle Detection', [
            'Core: DFS with recursion vs iterative. Color-marking for cycle detection (WHITE/GRAY/BLACK).',
            'Topological sort: Kahn\'s algorithm (BFS-based, in-degree) and DFS-based (reverse post-order).',
            'Problems: Course Schedule (LC 207), Course Schedule II (LC 210), Pacific Atlantic (LC 417), Number of Connected Components (LC 323), Redundant Connection (LC 684).',
            'Insight: Topological sort appears in build systems, dependency resolution, task scheduling — common at Amazon, Google.',
            'Practice goal: 5 problems. Implement both Kahn\'s algo and DFS topo sort.',
        ], '4 hrs'),
        ('DAY 17', 'Advanced Graphs: Dijkstra, Bellman-Ford', [
            'Dijkstra: Shortest path in weighted graph. Min-heap + dist array. O((V+E) log V).',
            'Bellman-Ford: Handles negative weights. O(VE). Detect negative cycles.',
            'Floyd-Warshall: All-pairs shortest path. O(V^3). Rarely in interviews but good to know.',
            'Problems: Network Delay Time (LC 743), Cheapest Flights Within K Stops (LC 787), Path with Minimum Effort (LC 1631), Swim in Rising Water (LC 778).',
            'Union-Find: Path compression + union by rank. Near O(1) amortized.',
            'Union-Find problems: Redundant Connection (LC 684), Number of Provinces (LC 547).',
            'Practice goal: 5 problems. Implement Dijkstra and Union-Find from scratch.',
        ], '4–5 hrs'),
        ('DAY 18', 'DP — 1D Patterns', [
            'Core: Memoization (top-down) vs tabulation (bottom-up). DP state design.',
            'Decision: At each step, what choices do I have? What does dp[i] represent?',
            'Patterns: Fibonacci-style, house robber, climbing stairs, coin change.',
            'Problems: Climbing Stairs (LC 70), House Robber (LC 198), House Robber II (LC 213), Coin Change (LC 322), Longest Increasing Subsequence (LC 300), Word Break (LC 139), Decode Ways (LC 91).',
            'LIS optimization: O(N log N) with patience sorting / binary search.',
            'Practice goal: 7 problems. Solve each with both memoization and tabulation.',
        ], '4 hrs'),
        ('DAY 19', 'DP — 2D & Subsequences', [
            'Core: 2D DP table. Rows = first sequence, cols = second sequence.',
            'Patterns: Longest Common Subsequence, Edit Distance, Matrix chain, Grid DP.',
            'Grid DP: dp[i][j] = ways to reach cell. Robot path counting, max gold in grid.',
            'Problems: Unique Paths (LC 62), Longest Common Subsequence (LC 1143), Edit Distance (LC 72), Longest Common Substring, Burst Balloons (LC 312), Regular Expression Matching (LC 10).',
            'Space optimization: 2D DP often reducible to O(N) space using rolling array.',
            'Practice goal: 6 problems. Implement LCS and Edit Distance from memory.',
        ], '4–5 hrs'),
        ('DAY 20', 'Greedy Algorithms', [
            'Core: Greedy choice property + optimal substructure. Prove greedy is optimal by exchange argument.',
            'Patterns: Interval scheduling, jump game, gas station, task assignment.',
            'Interval patterns: Sort by end time for max non-overlapping intervals (Greedy). Sort by start for merge intervals.',
            'Problems: Jump Game (LC 55), Jump Game II (LC 45), Gas Station (LC 134), Hand of Straights (LC 846), Merge Intervals (LC 56), Non-overlapping Intervals (LC 435), Meeting Rooms II (LC 253).',
            'Insight: Many greedy problems are disguised DP. Always ask: "Does making the locally optimal choice always lead to globally optimal?" Prove with exchange argument.',
            'Practice goal: 7 problems. Write the exchange argument for Interval Scheduling.',
        ], '4 hrs'),
        ('DAY 21', 'Week 3 Review & Graph/DP Mock', [
            'Morning: Code Dijkstra, Union-Find, and 1D DP template from memory.',
            'Afternoon: Full mock — 1 Graph Hard + 1 DP Medium in 90 minutes.',
            'Evening: Review all DP patterns. Create a personal DP pattern reference.',
            'Milestone: 70+ total problems solved. DP accuracy 75%+.',
            'Advanced: Study DP on Intervals, DP on Trees (Week 4 preview).',
        ], '5 hrs'),
    ]

    for day, topic, points, hrs in days_w3:
        story += [p(f'{day} — {topic}', S['h3']),
            p(f'<b>Estimated Time:</b> {hrs}', S['muted'])]
        for pt in points:
            story.append(p(f'• {pt}', S['bullet']))
        story.append(sp(3))

    story.append(PageBreak())

    # ── WEEK 4 ──────────────────────────────────────────────────────
    story += [p('WEEK 4 — ADVANCED TOPICS & MOCK INTERVIEWS', S['h1']), hr(ACCENT),
        p('Focus: Backtracking · Segment Trees · Hard Problems · Full Mock Interviews · Final Revision', S['cover_tag']),
        p('Goal: Handle Hards confidently. Simulate real FAANG interview conditions. Build interview stamina.', S['body']), sp(4)]

    days_w4 = [
        ('DAY 22', 'Backtracking', [
            'Core: State space tree exploration. Choose → Explore → Unchoose template.',
            'Template: def backtrack(state, choices): if goal: add to results; for choice in choices: make choice; backtrack(new_state); undo choice.',
            'Pruning: Constraint propagation. Sort choices to enable early termination.',
            'Problems: Subsets (LC 78), Subsets II (LC 90), Permutations (LC 46), Combination Sum (LC 39), N-Queens (LC 51), Sudoku Solver (LC 37), Word Search (LC 79).',
            'Insight: Backtracking time complexity is usually O(N! * N) or O(2^N * N). Always state this in interview.',
            'Practice goal: 7 problems. Code N-Queens with constraint propagation.',
        ], '4–5 hrs'),
        ('DAY 23', 'Segment Trees & Advanced DS', [
            'Core: Segment tree for range queries + point updates in O(log N). Build: O(N).',
            'Lazy propagation: Range updates in O(log N) by deferring computation.',
            'BIT (Fenwick Tree): Simpler O(log N) range sum. Binary indexed tree.',
            'Problems: Range Sum Query Mutable (LC 307), Count of Smaller Numbers After Self (LC 315), The Skyline Problem (LC 218), Burst Balloons (LC 312).',
            'Interview context: Segment trees appear rarely in FAANG coding rounds but commonly in system design and ML infra interviews. Know them conceptually deeply.',
            'Practice goal: 3 problems. Implement Segment Tree and BIT from scratch.',
        ], '4 hrs'),
        ('DAY 24', 'Hard Problem Sprint', [
            'Strategy: Hard problems are usually combination of 2–3 Medium patterns. Identify components.',
            'Approach: 10 min to identify pattern. 25 min to code. 5 min to verify.',
            'Problems: Trapping Rain Water II (LC 407), Median of Two Sorted Arrays (LC 4), Word Ladder II (LC 126), Alien Dictionary (LC 269), Maximum Flow (LC 1929), Minimum Cost to Connect All Points (LC 1584 — Prim\'s/Kruskal\'s).',
            'If stuck in interview: Narrate what you know. Partial solution > silence. Pseudocode is acceptable.',
            'Practice goal: 3–4 Hards. Time yourself. Document your thought process.',
        ], '5 hrs'),
        ('DAY 25', 'Full Mock Interview Day 1', [
            'Session 1 (90 min): 2 coding problems (1 Medium, 1 Hard). Camera on. Narrate everything.',
            'Session 2 (60 min): System design component (review after this week).',
            'Debrief: Record time-to-first-approach, time-to-code, bugs found, communication quality.',
            'Platforms: interviewing.io, Pramp, or peer mock with another engineer.',
            'Self-assessment: Rate yourself 1–10 on: communication, correctness, optimization, edge cases.',
        ], '4–5 hrs'),
        ('DAY 26', 'Contest Strategy & Speed Training', [
            'Timed contest drill: LeetCode Weekly Contest format — 4 problems in 90 minutes.',
            'Strategy: Problem 1 (Easy) in 5 min. Problem 2 (Medium) in 20 min. Problem 3 (Medium-Hard) in 30 min. Problem 4 (Hard) in remaining time.',
            'If stuck on Problem 4: Submit brute force for partial credit, move on, come back.',
            'Pattern recognition speed: Practice "flash card" — see a problem title, state the pattern in 30 seconds.',
            'Problems: Complete 1 full Weekly Contest (latest or recent ones on LeetCode).',
            'Practice goal: Finish top 3 problems in contest. Review editorial for all 4.',
        ], '4 hrs'),
        ('DAY 27', 'Blind 75 & NeetCode 150 Final Review', [
            'Blind 75: Go through all 75 problems. For each: state the pattern, state Big-O, pseudocode in 2 min.',
            'NeetCode 150: Identify the 30 problems you haven\'t done. Speed-solve them in batches by category.',
            'Focus areas: Any problem you\'ve solved fewer than 2 times.',
            'Interview patterns mastery: Two Sum family, BFS/DFS, DP 1D/2D, Monotonic Stack, Binary Search on answer.',
            'Practice goal: 10 speed-reviews from Blind 75. 5 new from NeetCode 150.',
        ], '5 hrs'),
        ('DAY 28', 'Final Mock & Interview Day Strategy', [
            'Full mock: 2 back-to-back coding rounds (60 min each) simulating FAANG loop.',
            'Interview-day checklist: Sleep 8 hrs. No new concepts. Review cheat sheet. Warm up with 1 Easy.',
            'Communication: "I\'m thinking about..." "One edge case to consider is..." "Can I optimize this further?"',
            'If you blank: "Let me think about a simpler version first." Break problem down.',
            'After each round: Note what went well and one improvement.',
            'Milestone: 100+ problems solved. Hard accuracy 50%+. Mocks feeling comfortable.',
        ], '5 hrs'),
    ]

    for day, topic, points, hrs in days_w4:
        story += [p(f'{day} — {topic}', S['h3']),
            p(f'<b>Estimated Time:</b> {hrs}', S['muted'])]
        for pt in points:
            story.append(p(f'• {pt}', S['bullet']))
        story.append(sp(3))

    story.append(PageBreak())

    # ── FAANG TOP PATTERNS ──────────────────────────────────────────
    story += [p('TOP 20 FAANG DSA PATTERNS', S['h1']), hr(ACCENT), sp(4)]
    patterns = [
        ('1. Two Sum / HashMap Lookup', 'O(N)', 'LC 1, 15, 454', 'High'),
        ('2. Sliding Window (Fixed)', 'O(N)', 'LC 643, 567, 1004', 'High'),
        ('3. Sliding Window (Variable)', 'O(N)', 'LC 3, 76, 424', 'High'),
        ('4. Two Pointers (Sorted)', 'O(N)', 'LC 167, 11, 42', 'High'),
        ('5. Binary Search on Answer', 'O(N log N)', 'LC 875, 1011, 410', 'High'),
        ('6. BFS Shortest Path', 'O(V+E)', 'LC 994, 127, 1091', 'High'),
        ('7. DFS + Backtracking', 'O(2^N)', 'LC 78, 39, 51', 'High'),
        ('8. Topological Sort', 'O(V+E)', 'LC 207, 210, 269', 'High'),
        ('9. Union-Find', 'O(α(N))', 'LC 684, 547, 1061', 'Medium'),
        ('10. Merge Intervals', 'O(N log N)', 'LC 56, 435, 253', 'High'),
        ('11. 1D DP (Linear)', 'O(N)', 'LC 70, 198, 300', 'High'),
        ('12. 2D DP / Grid DP', 'O(N*M)', 'LC 62, 1143, 72', 'High'),
        ('13. Monotonic Stack', 'O(N)', 'LC 739, 84, 85', 'Medium'),
        ('14. Heap / Priority Queue', 'O(N log K)', 'LC 215, 347, 295', 'High'),
        ('15. Trie Prefix Search', 'O(L)', 'LC 208, 211, 212', 'Medium'),
        ('16. Dijkstra\'s SSSP', 'O((V+E)log V)', 'LC 743, 787, 1631', 'Medium'),
        ('17. Segment Tree / BIT', 'O(N log N)', 'LC 307, 315', 'Low-Med'),
        ('18. Fast & Slow Pointers', 'O(N)', 'LC 142, 287, 876', 'High'),
        ('19. Prefix Sum + HashMap', 'O(N)', 'LC 560, 523, 325', 'High'),
        ('20. Matrix DFS/BFS', 'O(N*M)', 'LC 200, 130, 417', 'High'),
    ]
    pat_data = [['Pattern', 'Complexity', 'Key LCs', 'Priority']] + patterns
    story.append(Table(pat_data, colWidths=[140, 70, 100, 55],
        style=dark_table_style(ACCENT)))
    story.append(PageBreak())

    # ── RESOURCES ───────────────────────────────────────────────────
    story += [p('RESOURCES & STUDY MATERIALS', S['h1']), hr(ACCENT), sp(4)]

    res_sections = [
        ('Books', [
            'Cracking the Coding Interview — Gayle Laakmann McDowell (foundational)',
            'Elements of Programming Interviews in Python — Aziz, Lee, Prakash (FAANG-focused)',
            'Algorithm Design Manual — Skiena (deep theory)',
            'Introduction to Algorithms (CLRS) — Cormen et al. (academic reference)',
        ]),
        ('YouTube Channels', [
            'NeetCode — Best visual explanations of Blind 75 + NeetCode 150',
            'Abdul Bari — Deep algorithmic theory with proofs',
            'Errichto — Competitive programming, advanced algorithms',
            'Back to Back SWE — FAANG interview walkthroughs',
            'William Fiset — Graph algorithms, data structures',
            'AlgoExpert Video Solutions — Premium but excellent walkthroughs',
        ]),
        ('LeetCode Lists', [
            'Blind 75: https://www.teamblind.com/post/New-Year-Gift---Curated-List-of-Top-75-LeetCode-Questions',
            'NeetCode 150: https://neetcode.io/practice',
            'LeetCode Top Interview 150: https://leetcode.com/studyplan/top-interview-150/',
            'LeetCode Company Tags: Google, Meta, Amazon, Microsoft (Premium)',
            'Grind 75: https://www.techinterviewhandbook.org/grind75',
        ]),
        ('GitHub Repos', [
            'github.com/neetcode-gh/leetcode — NeetCode Python solutions',
            'github.com/azl397985856/leetcode — Comprehensive solutions with explanations',
            'github.com/labuladong/fucking-algorithm — Algorithm thinking patterns',
            'github.com/TheAlgorithms/Python — All algorithms in Python',
        ]),
        ('Practice Platforms', [
            'LeetCode (primary) — leetcode.com',
            'HackerRank (assessment simulation) — hackerrank.com',
            'Codeforces (competitive programming warmup) — codeforces.com',
            'AlgoExpert — curated 160 problems with video — algoexpert.io',
            'Pramp (peer mock interviews) — pramp.com',
        ]),
    ]

    for sec, items in res_sections:
        story.append(p(sec, S['h3']))
        for item in items:
            story.append(p(f'• {item}', S['bullet']))
        story.append(sp(3))

    story.append(PageBreak())

    # ── CHEAT SHEET ──────────────────────────────────────────────────
    story += [p('FINAL CHEAT SHEET', S['h1']), hr(ACCENT), sp(4)]

    story += [p('Python DSA Quick Reference', S['h2']),
        p('from collections import defaultdict, Counter, deque', S['code']),
        p('import heapq  # min-heap; use -val for max-heap', S['code']),
        p('# Two Sum\ndef two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen: return [seen[target-n], i]\n        seen[n] = i', S['code']),
        p('# Binary Search (leftmost)\ndef bs_left(nums, target):\n    lo, hi = 0, len(nums)\n    while lo < hi:\n        mid = (lo + hi) // 2\n        if nums[mid] < target: lo = mid + 1\n        else: hi = mid\n    return lo', S['code']),
        p('# BFS Template\nfrom collections import deque\ndef bfs(graph, start):\n    q, visited = deque([start]), {start}\n    while q:\n        node = q.popleft()\n        for nei in graph[node]:\n            if nei not in visited:\n                visited.add(nei); q.append(nei)', S['code']),
        p('# Backtracking Template\ndef backtrack(state, choices, results):\n    if is_goal(state): results.append(state[:]); return\n    for c in choices:\n        state.append(c)\n        backtrack(state, new_choices(c), results)\n        state.pop()', S['code']),
        sp(4)]

    story += [p('Interview-Day Checklist', S['h3'])]
    checklist = [
        '☐ Read problem twice before writing any code',
        '☐ Clarify: input size, data types, edge cases, expected output format',
        '☐ State brute-force complexity first, then optimize',
        '☐ Name the pattern out loud ("this looks like a sliding window problem")',
        '☐ Write clean code with meaningful variable names',
        '☐ Narrate your thought process continuously',
        '☐ Dry-run your code with the given example',
        '☐ Test edge cases: empty input, single element, duplicates, negatives',
        '☐ State final Big-O for time AND space',
        '☐ Offer further optimizations even if not asked',
    ]
    for item in checklist:
        story.append(p(item, S['bullet']))

    story += [sp(8), p('Weekly Progress Milestones', S['h3'])]
    milestones = [
        ['Week', 'Problems Solved', 'Target Accuracy', 'Key Milestone'],
        ['Week 1', '25–30', '90% Easy, 70% Med', 'All basic patterns from memory'],
        ['Week 2', '20–25 (45 total)', '80% Med', 'All DS implementations from memory'],
        ['Week 3', '25–30 (70 total)', '75% Med, 40% Hard', 'DP + Graph patterns fluent'],
        ['Week 4', '30+ (100 total)', '85% Med, 50% Hard', 'Mock interviews passing bar'],
    ]
    story.append(Table(milestones, colWidths=[50, 100, 110, 115],
        style=dark_table_style(ACCENT)))

    return story

story = make_story()
build_doc(OUT, story, TITLE, ACCENT)
print(f'Created: {OUT}')

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    HRFlowable, KeepTogether, Preformatted
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import ListFlowable, ListItem
import textwrap

OUTPUT = "/mnt/user/outputs/LLM_Engineering_Complete_Guide.pdf"

# ── Colour palette ──────────────────────────────────────────────────────────
C_BG       = colors.HexColor("#0F172A")   # dark navy  – section banners
C_ACCENT   = colors.HexColor("#6366F1")   # indigo     – headings
C_ACCENT2  = colors.HexColor("#10B981")   # emerald    – sub-accents
C_CODE_BG  = colors.HexColor("#1E293B")   # slate      – code blocks
C_CODE_FG  = colors.HexColor("#E2E8F0")   # light grey – code text
C_NOTE_BG  = colors.HexColor("#EEF2FF")   # soft indigo – callout boxes
C_WARN_BG  = colors.HexColor("#FEF3C7")   # amber      – tip boxes
C_H2       = colors.HexColor("#4F46E5")   # deep indigo
C_H3       = colors.HexColor("#059669")   # green
C_TEXT     = colors.HexColor("#1E293B")
C_MUTED    = colors.HexColor("#64748B")
C_WHITE    = colors.white
C_BORDER   = colors.HexColor("#CBD5E1")

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=letter,
    rightMargin=0.75*inch,
    leftMargin=0.75*inch,
    topMargin=0.75*inch,
    bottomMargin=0.75*inch,
)

W = letter[0] - 1.5*inch   # usable width

styles = getSampleStyleSheet()

# ── Custom styles ────────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

sty = {
    "cover_title": S("cover_title",
        fontSize=36, leading=44, textColor=C_WHITE,
        fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=12),
    "cover_sub": S("cover_sub",
        fontSize=16, leading=22, textColor=colors.HexColor("#A5B4FC"),
        fontName="Helvetica", alignment=TA_CENTER, spaceAfter=6),
    "cover_tag": S("cover_tag",
        fontSize=11, leading=16, textColor=colors.HexColor("#94A3B8"),
        fontName="Helvetica", alignment=TA_CENTER),
    "part_title": S("part_title",
        fontSize=22, leading=28, textColor=C_WHITE,
        fontName="Helvetica-Bold", alignment=TA_CENTER),
    "h1": S("h1",
        fontSize=18, leading=24, textColor=C_ACCENT,
        fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=8,
        borderPad=4),
    "h2": S("h2",
        fontSize=14, leading=20, textColor=C_H2,
        fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6),
    "h3": S("h3",
        fontSize=12, leading=16, textColor=C_H3,
        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4),
    "body": S("body",
        fontSize=10, leading=16, textColor=C_TEXT,
        fontName="Helvetica", spaceAfter=6, alignment=TA_JUSTIFY),
    "bullet": S("bullet",
        fontSize=10, leading=15, textColor=C_TEXT,
        fontName="Helvetica", leftIndent=16, spaceAfter=3,
        bulletIndent=4),
    "code": S("code",
        fontSize=8.2, leading=12, textColor=C_CODE_FG,
        fontName="Courier", backColor=C_CODE_BG,
        leftIndent=10, rightIndent=10,
        spaceBefore=4, spaceAfter=4,
        borderPad=6),
    "code_label": S("code_label",
        fontSize=8, leading=10, textColor=colors.HexColor("#94A3B8"),
        fontName="Helvetica-Bold", spaceBefore=8),
    "note": S("note",
        fontSize=9.5, leading=14, textColor=colors.HexColor("#312E81"),
        fontName="Helvetica", leftIndent=8),
    "tip": S("tip",
        fontSize=9.5, leading=14, textColor=colors.HexColor("#92400E"),
        fontName="Helvetica", leftIndent=8),
    "toc_h": S("toc_h",
        fontSize=11, leading=18, textColor=C_ACCENT,
        fontName="Helvetica-Bold", leftIndent=0, spaceAfter=2),
    "toc_item": S("toc_item",
        fontSize=9.5, leading=15, textColor=C_TEXT,
        fontName="Helvetica", leftIndent=16, spaceAfter=1),
    "caption": S("caption",
        fontSize=8.5, leading=12, textColor=C_MUTED,
        fontName="Helvetica-Oblique", alignment=TA_CENTER, spaceBefore=2),
    "mono_inline": S("mono_inline",
        fontSize=9, leading=13, textColor=C_TEXT,
        fontName="Courier"),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def section_banner(title, subtitle=""):
    """Full-width dark banner for a major section."""
    inner = [Paragraph(title, sty["part_title"])]
    if subtitle:
        inner.append(Paragraph(subtitle, S("_ps", fontSize=11, leading=16,
            textColor=colors.HexColor("#94A3B8"), fontName="Helvetica",
            alignment=TA_CENTER)))
    t = Table([[inner]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), C_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 18),
        ("BOTTOMPADDING", (0,0), (-1,-1), 18),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
        ("ROUNDEDCORNERS", [6]),
    ]))
    return t

def code_block(code_str, label="Python"):
    items = []
    if label:
        items.append(Paragraph(f"▸ {label}", sty["code_label"]))
    # Use Preformatted directly (it can split across pages unlike a Table)
    items.append(Preformatted(code_str, sty["code"]))
    return items

def note_box(text, kind="note"):
    bg = C_NOTE_BG if kind=="note" else C_WARN_BG
    icon = "💡" if kind=="tip" else "ℹ"
    st = sty["note"] if kind=="note" else sty["tip"]
    p = Paragraph(f"<b>{icon}</b>  {text}", st)
    t = Table([[p]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), bg),
        ("LEFTPADDING",   (0,0), (-1,-1), 14),
        ("RIGHTPADDING",  (0,0), (-1,-1), 14),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("BOX", (0,0), (-1,-1), 0.5, C_BORDER),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=C_BORDER,
                      spaceAfter=6, spaceBefore=6)

def h1(txt): return Paragraph(txt, sty["h1"])
def h2(txt): return Paragraph(txt, sty["h2"])
def h3(txt): return Paragraph(txt, sty["h3"])
def p(txt):  return Paragraph(txt, sty["body"])
def sp(n=6): return Spacer(1, n)
def bul(items):
    return [Paragraph(f"• &nbsp; {i}", sty["bullet"]) for i in items]

def kv_table(rows, col1=2.2*inch):
    data = [[Paragraph(f"<b>{k}</b>", sty["body"]),
             Paragraph(v, sty["body"])] for k,v in rows]
    t = Table(data, colWidths=[col1, W-col1])
    t.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("ROWBACKGROUNDS",(0,0), (-1,-1),
         [colors.HexColor("#F8FAFC"), colors.white]),
        ("BOX",           (0,0), (-1,-1), 0.4, C_BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, C_BORDER),
    ]))
    return t

# ════════════════════════════════════════════════════════════════════════════
# CONTENT BUILDER
# ════════════════════════════════════════════════════════════════════════════
story = []

# ── COVER PAGE ────────────────────────────────────────────────────────────────
cover_bg = Table(
    [[Paragraph("LLM Engineering", sty["cover_title"])],
     [Paragraph("Complete Guide", sty["cover_title"])],
     [sp(8)],
     [Paragraph("From Fundamentals to Production", sty["cover_sub"])],
     [sp(6)],
     [Paragraph("Beginner → Advanced AI Engineering", sty["cover_tag"])],
     [sp(4)],
     [Paragraph("LLM Fundamentals · Prompt Engineering · Fine-Tuning · RAG · Context Engineering · AI Agents · MCP · Production", sty["cover_tag"])],
    ],
    colWidths=[W]
)
cover_bg.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), C_BG),
    ("TOPPADDING",    (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING",   (0,0), (-1,-1), 30),
    ("RIGHTPADDING",  (0,0), (-1,-1), 30),
    ("ROUNDEDCORNERS", [10]),
]))
story += [sp(60), cover_bg, sp(40)]
story.append(hr())
story.append(Paragraph(
    "A comprehensive reference for AI engineers covering every major concept "
    "with real-world examples and production-ready code.",
    S("_ci", fontSize=10, leading=15, textColor=C_MUTED,
      fontName="Helvetica-Oblique", alignment=TA_CENTER)))
story.append(PageBreak())

# ── TABLE OF CONTENTS ─────────────────────────────────────────────────────────
story.append(h1("📋  Table of Contents"))
story.append(hr())
toc_data = [
    ("Part 1", "LLM Fundamentals",
     ["Next-token prediction", "7 Generation parameters", "Transformer vs MoE", "Running LLMs locally"]),
    ("Part 2", "Prompt Engineering",
     ["3 Reasoning techniques", "JSON prompting", "Verbalized sampling"]),
    ("Part 3", "Fine-tuning Techniques",
     ["LoRA from scratch", "GRPO for reasoning models", "Custom datasets", "SFT vs RFT"]),
    ("Part 4", "RAG Systems",
     ["8 RAG architectures", "5 Chunking strategies", "RAG vs Agentic RAG vs REFRAG", "When to choose"]),
    ("Part 5", "Context Engineering",
     ["6 types of context", "Production workflows", "Manual vs Agentic RAG"]),
    ("Part 6", "AI Agents",
     ["ReAct pattern", "5 levels of agentic AI", "7 multi-agent patterns", "Agent2Agent protocol", "Memory types"]),
    ("Part 7", "MCP Protocol",
     ["Fundamentals", "MCP vs APIs vs Function calling", "Clients & servers", "Avoiding tool overload"]),
    ("Part 8", "Production & Deployment",
     ["Model compression", "KV caching", "Multi-turn evals", "vLLM & LitServe", "Observability"]),
]
for part, title, items in toc_data:
    story.append(Paragraph(f"<b>{part} — {title}</b>", sty["toc_h"]))
    for it in items:
        story.append(Paragraph(f"◦  {it}", sty["toc_item"]))
    story.append(sp(4))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 1 — LLM FUNDAMENTALS
# ════════════════════════════════════════════════════════════════════════════
story.append(section_banner("Part 1 — LLM Fundamentals",
    "How language models think, generate, and are deployed"))
story.append(sp(12))

story.append(h1("1.1  How LLMs Predict the Next Token"))
story.append(p(
    "Large Language Models are fundamentally <b>next-token predictors</b>. "
    "Given a sequence of tokens (sub-word pieces), the model outputs a "
    "probability distribution over its entire vocabulary for the very next token. "
    "Training minimises cross-entropy loss over billions of such predictions, "
    "forcing the model to compress a vast understanding of language and world knowledge "
    "into its weights."
))
story.append(h2("The Pipeline"))
story += bul([
    "<b>Tokenisation</b> – Raw text is split into sub-word tokens via BPE or SentencePiece. "
    "\"unbelievable\" might become [\"un\", \"believ\", \"able\"].",
    "<b>Embedding</b> – Each token ID is looked up in a learned embedding matrix (d_model dimensions).",
    "<b>Positional encoding</b> – Position information is added (sinusoidal or learned RoPE/ALiBi).",
    "<b>Transformer blocks</b> – N stacked blocks of multi-head self-attention + feed-forward layers.",
    "<b>LM Head</b> – A linear layer projects the final hidden state to vocabulary logits.",
    "<b>Softmax</b> – Logits → probabilities. The token with highest probability (or a sampled one) is appended.",
])
story.append(sp(6))
story += code_block(
"""import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "meta-llama/Llama-3.2-1B"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16)

prompt = "The capital of France is"
inputs = tokenizer(prompt, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)          # forward pass
    logits  = outputs.logits           # shape: (batch, seq_len, vocab_size)

# Probabilities for the NEXT token (last position)
next_token_logits = logits[0, -1, :]
probs = F.softmax(next_token_logits, dim=-1)

# Top-5 predictions
top5 = torch.topk(probs, 5)
for prob, idx in zip(top5.values, top5.indices):
    token = tokenizer.decode([idx])
    print(f"  {token!r:15s} {prob.item():.4f}")
# Output:
#  ' Paris'         0.8821
#  ' Lyon'          0.0312
#  ' Marseille'     0.0187
#  ' Nice'          0.0094
#  ' Bordeaux'      0.0063
""")
story.append(sp(8))

story.append(h1("1.2  7 Generation Parameters"))
story.append(p(
    "Sampling parameters control how the model turns logit distributions into actual text. "
    "Understanding them is essential for getting consistent, creative, or factual output."
))

params_data = [
    ("temperature",   "Scales logits before softmax. <b>Low (0.1–0.5)</b>: deterministic/factual. "
                      "<b>High (0.8–1.5)</b>: creative/diverse. At 0 → greedy decoding."),
    ("top_p",         "(Nucleus sampling) Keep the smallest set of tokens whose cumulative probability "
                      "≥ p. Typical: 0.9. Cuts out unlikely long-tail tokens dynamically."),
    ("top_k",         "Keep only the k most probable tokens at each step. Typical: 40–100. "
                      "Simple but less adaptive than top_p."),
    ("min_p",         "Filter tokens with probability < min_p × max_prob. More stable than top_p "
                      "at high temperatures. Recommended: 0.05–0.1."),
    ("repetition_penalty", "Divides logit of already-seen tokens. >1.0 discourages repetition. "
                           "Typical: 1.1–1.3. Too high → incoherence."),
    ("max_new_tokens","Hard cap on generated tokens. Prevents runaway generation."),
    ("stop sequences","Strings that halt generation immediately (e.g. [\"</s>\", \"\\n\\n\", \"###\"]). "
                      "Essential for structured outputs."),
]
story.append(kv_table(params_data))
story.append(sp(8))

story += code_block(
"""from transformers import pipeline

gen = pipeline("text-generation", model="meta-llama/Llama-3.2-1B")

# Deterministic (factual Q&A)
out = gen("What is photosynthesis?",
          max_new_tokens=80,
          temperature=0.1,
          do_sample=True,
          top_p=0.9,
          repetition_penalty=1.1)

# Creative writing
out = gen("Write a haiku about quantum mechanics:",
          max_new_tokens=40,
          temperature=1.2,
          top_p=0.95,
          top_k=80,
          do_sample=True)

# Structured output with stop sequence
out = gen('Return JSON with key "answer": The color of the sky is',
          max_new_tokens=30,
          temperature=0.0,
          stop_strings=["}"])
""")
story.append(sp(8))

story.append(h1("1.3  Transformer vs Mixture of Experts (MoE)"))
story.append(h2("Dense Transformer"))
story.append(p(
    "Every input token flows through <b>all</b> parameters in every layer. "
    "A block contains: (1) Multi-Head Self-Attention (MHSA), (2) Feed-Forward Network (FFN). "
    "For a model with d_model=4096 and 32 layers, every token uses ~7B parameters."
))
story += code_block(
"""# Simplified Transformer Block
import torch, torch.nn as nn, math

class TransformerBlock(nn.Module):
    def __init__(self, d_model=512, n_heads=8, d_ff=2048, dropout=0.1):
        super().__init__()
        self.attn  = nn.MultiheadAttention(d_model, n_heads, dropout=dropout, batch_first=True)
        self.ff    = nn.Sequential(
            nn.Linear(d_model, d_ff), nn.GELU(), nn.Linear(d_ff, d_model))
        self.ln1   = nn.LayerNorm(d_model)
        self.ln2   = nn.LayerNorm(d_model)
        self.drop  = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # Self-attention with residual
        attn_out, _ = self.attn(x, x, x, attn_mask=mask)
        x = self.ln1(x + self.drop(attn_out))
        # Feed-forward with residual
        x = self.ln2(x + self.drop(self.ff(x)))
        return x
""")

story.append(h2("Mixture of Experts (MoE)"))
story.append(p(
    "MoE replaces the single FFN with <b>E expert FFNs</b> and a <b>router</b> that selects "
    "the top-K experts per token. Only K/E fraction of parameters are activated per token — "
    "massive efficiency. GPT-4, Mixtral, Qwen-MoE all use this architecture."
))
story += bul([
    "<b>Total params</b>: huge (e.g. Mixtral 8x7B = 46.7B total)",
    "<b>Active params per token</b>: small (Mixtral activates ~12.9B of 46.7B)",
    "<b>Router</b>: a small linear layer that outputs softmax weights over experts",
    "<b>Load balancing loss</b>: extra term to prevent all tokens routing to same expert",
])
story += code_block(
"""class MoELayer(nn.Module):
    def __init__(self, d_model=512, d_ff=2048, n_experts=8, top_k=2):
        super().__init__()
        self.experts = nn.ModuleList(
            [nn.Sequential(nn.Linear(d_model, d_ff), nn.GELU(),
                           nn.Linear(d_ff, d_model))
             for _ in range(n_experts)])
        self.router  = nn.Linear(d_model, n_experts)
        self.top_k   = top_k

    def forward(self, x):
        # x: (batch, seq, d_model)
        B, S, D = x.shape
        x_flat = x.view(-1, D)                           # (B*S, D)
        logits  = self.router(x_flat)                    # (B*S, E)
        weights, indices = torch.topk(logits, self.top_k, dim=-1)
        weights = torch.softmax(weights, dim=-1)         # normalise

        out = torch.zeros_like(x_flat)
        for k in range(self.top_k):
            expert_ids = indices[:, k]                   # (B*S,)
            w          = weights[:, k].unsqueeze(-1)     # (B*S, 1)
            for e_idx in range(len(self.experts)):
                mask = (expert_ids == e_idx)
                if mask.any():
                    out[mask] += w[mask] * self.experts[e_idx](x_flat[mask])
        return out.view(B, S, D)
""")
story.append(note_box(
    "MoE shines at inference throughput — same latency as a smaller dense model but "
    "much higher quality, because total capacity is larger. The trade-off is higher "
    "memory to hold all expert weights.", "note"))
story.append(sp(8))

story.append(h1("1.4  Running LLMs Locally for Development"))
story.append(h2("Option A — llama.cpp / Ollama (CPU-friendly, GGUF)"))
story += code_block(
"""# Install Ollama (macOS / Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Pull and run a model
ollama pull llama3.2:3b
ollama run llama3.2:3b "Explain backpropagation in 3 sentences"

# Serve via REST API (compatible with OpenAI SDK)
ollama serve    # starts on http://localhost:11434
""", "Shell")
story += code_block(
"""from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
resp = client.chat.completions.create(
    model="llama3.2:3b",
    messages=[{"role":"user","content":"What is gradient descent?"}],
    temperature=0.3)
print(resp.choices[0].message.content)
""")

story.append(h2("Option B — Transformers + bitsandbytes (4-bit quantisation)"))
story += code_block(
"""pip install transformers bitsandbytes accelerate
""", "Shell")
story += code_block(
"""from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",          # NormalFloat4 – best accuracy
    bnb_4bit_compute_dtype=torch.bfloat16,
)
model_id = "meta-llama/Llama-3.1-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto"
)
# ~5 GB VRAM instead of ~16 GB
""")
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 2 — PROMPT ENGINEERING
# ════════════════════════════════════════════════════════════════════════════
story.append(section_banner("Part 2 — Prompt Engineering",
    "Designing inputs that reliably extract the model's best reasoning"))
story.append(sp(12))

story.append(h1("2.1  Three Reasoning Techniques"))

story.append(h2("Chain-of-Thought (CoT)"))
story.append(p(
    "Asking the model to reason step-by-step before answering dramatically improves accuracy "
    "on arithmetic, commonsense, and multi-step tasks. The magic phrase <b>\"Let's think step by step\"</b> "
    "alone (zero-shot CoT) boosts performance significantly."
))
story += code_block(
"""# Zero-shot CoT
PROMPT = \"\"\"
Q: A train travels 300 km in 2.5 hours, then stops for 30 minutes,
   then travels 150 km in 1 hour. What is the average speed for the
   entire journey?

Let's think step by step.
\"\"\"

# Few-shot CoT (provide worked examples)
PROMPT = \"\"\"
Q: If 5 cats catch 5 mice in 5 minutes, how many cats are needed
   to catch 100 mice in 100 minutes?
A: Step 1 – Rate per cat: 1 cat catches 1 mouse in 5 minutes.
   Step 2 – In 100 minutes, 1 cat catches 100/5 = 20 mice.
   Step 3 – For 100 mice: 100 / 20 = 5 cats.
   Answer: 5

Q: A factory produces 200 units per day. A new machine increases
   production by 35%. How many units per week after the upgrade?
A:\"\"\"
""")

story.append(h2("Self-Consistency"))
story.append(p(
    "Sample multiple diverse reasoning paths (temperature > 0) then take the <b>majority vote</b> "
    "on the final answer. This ensemble approach reduces variance without ensembling entire models."
))
story += code_block(
"""from collections import Counter
from openai import OpenAI

client = OpenAI()

def self_consistent_answer(question: str, n_samples: int = 5) -> str:
    answers = []
    for _ in range(n_samples):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content":
                 "Reason step by step, then output ANSWER: <your answer>"},
                {"role": "user", "content": question},
            ],
            temperature=0.8,          # diversity between paths
        )
        text = resp.choices[0].message.content
        # Extract final answer
        if "ANSWER:" in text:
            ans = text.split("ANSWER:")[-1].strip().split("\\n")[0]
            answers.append(ans)
    # Majority vote
    return Counter(answers).most_common(1)[0][0]

result = self_consistent_answer(
    "What is 17% of 340, rounded to the nearest integer?")
print(result)   # → 58
""")

story.append(h2("ReAct (Reason + Act)"))
story.append(p(
    "The model interleaves <b>Thought</b> (reasoning), <b>Action</b> (tool call), and "
    "<b>Observation</b> (tool result) steps. Covered in depth in Part 6 (AI Agents)."
))
story += code_block(
"""SYSTEM = \"\"\"You are an assistant with access to tools.
Use the format:
Thought: <your reasoning>
Action: <tool_name>(<args>)
Observation: <result>
... (repeat as needed)
Final Answer: <answer>

Available tools:
- search(query) – web search
- calculator(expr) – evaluate math
\"\"\"

USER = "What is the GDP of Germany multiplied by the population of Brazil?"

# Model might produce:
# Thought: I need Germany's GDP and Brazil's population.
# Action: search("Germany GDP 2024")
# Observation: Germany GDP = $4.46 trillion
# Action: search("Brazil population 2024")
# Observation: Brazil population = 215 million
# Action: calculator("4.46e12 * 215e6")
# Observation: 9.589e20
# Final Answer: ~9.59 × 10^20 USD·people
""")
story.append(sp(8))

story.append(h1("2.2  JSON Prompting for Structured Outputs"))
story.append(p(
    "Reliable structured output is critical for production pipelines. "
    "Three strategies in increasing reliability:"
))
story.append(h2("Strategy 1 – Prompt-only JSON"))
story += code_block(
"""SYSTEM = \"\"\"You are a data extraction API.
Always respond with valid JSON only. No prose, no markdown fences.
Schema: {"name": str, "age": int, "skills": [str], "experience_years": int}
\"\"\"
USER = "Extract data: John Doe, 32, works with Python and Kubernetes, 8 years exp."
# Works ~85% of the time with capable models
""")

story.append(h2("Strategy 2 – Structured Outputs (OpenAI / Instructor)"))
story += code_block(
"""from pydantic import BaseModel, Field
from typing import List
import instructor
from openai import OpenAI

class Candidate(BaseModel):
    name: str
    age: int
    skills: List[str]
    experience_years: int = Field(ge=0, le=50)
    seniority: str = Field(description="junior | mid | senior | staff")

client = instructor.from_openai(OpenAI())

candidate = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=Candidate,
    messages=[
        {"role": "system", "content": "Extract candidate information."},
        {"role": "user",   "content":
         "Jane Smith, 28, expert in React, Node.js, and GraphQL, 5 years"},
    ]
)
print(candidate.model_dump())
# {'name': 'Jane Smith', 'age': 28, 'skills': ['React','Node.js','GraphQL'],
#  'experience_years': 5, 'seniority': 'mid'}
""")

story.append(h2("Strategy 3 – Grammar-constrained Decoding (llama.cpp)"))
story += code_block(
"""# llama.cpp forces output to match a JSON schema via GBNF grammar
# This gives 100% valid JSON regardless of model capability

from llama_cpp import Llama
from llama_cpp.llama_types import JsonType

llm = Llama(model_path="llama-3.2-3b.gguf", n_ctx=2048)

schema = {
    "type": "object",
    "properties": {
        "sentiment": {"type": "string", "enum": ["positive","neutral","negative"]},
        "confidence": {"type": "number"},
        "keywords": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["sentiment", "confidence", "keywords"]
}

response = llm.create_chat_completion(
    messages=[{"role":"user","content":"Analyse: 'Amazing product, love it!'"}],
    response_format={"type": "json_object", "schema": schema}
)
# Always valid JSON — guaranteed by the grammar sampler
""")
story.append(sp(8))

story.append(h1("2.3  Verbalized Sampling Strategies"))
story.append(p(
    "Instead of (or in addition to) adjusting numeric sampling parameters, "
    "you can describe the desired distribution <i>in words</i>."
))
story += code_block(
"""# Tell the model HOW to generate
PROMPTS = {

    "greedy_like": \"\"\"
        Answer with the single most factually accurate response.
        Do not speculate or offer alternatives.\"\"\",

    "diverse":  \"\"\"
        Generate a creative, unexpected response. Avoid the most
        obvious answer. Think laterally.\"\"\",

    "calibrated": \"\"\"
        Rate your confidence (0-100%) before answering.
        If confidence < 70%, list the main uncertainties.\"\"\",

    "beam_like": \"\"\"
        Give me the 3 most likely answers ranked by probability,
        with a brief justification for each.\"\"\",

    "temperature_metaphor": \"\"\"
        Respond as if you're brainstorming freely — wild ideas are
        welcome, quantity over precision.\"\"\",
}

# Example — calibrated uncertainty
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role":"system","content": PROMPTS["calibrated"]},
        {"role":"user",  "content": "Who invented the telephone?"}
    ],
    temperature=0.1
)
# Model might output:
# Confidence: 85%
# Answer: Alexander Graham Bell received the first patent (1876), though
# Elisha Gray filed hours later and Antonio Meucci had an earlier caveat.
# Uncertainty: contested historical priority between multiple inventors.
""")
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 3 — FINE-TUNING
# ════════════════════════════════════════════════════════════════════════════
story.append(section_banner("Part 3 — Fine-Tuning Techniques",
    "LoRA, GRPO, dataset generation, SFT vs RFT"))
story.append(sp(12))

story.append(h1("3.1  LoRA (Low-Rank Adaptation) From Scratch"))
story.append(p(
    "LoRA freezes the original model weights W and adds trainable low-rank matrices "
    "ΔW = B·A (where B ∈ R^{d×r}, A ∈ R^{r×k}, r << min(d,k)). "
    "Only A and B are trained — typically 0.1–1% of original parameters."
))
story += code_block(
"""import torch, torch.nn as nn, math

class LoRALinear(nn.Module):
    \"\"\"Drop-in replacement for nn.Linear with LoRA.\"\"\"
    def __init__(self, in_features, out_features,
                 rank=8, alpha=16, dropout=0.05):
        super().__init__()
        self.rank  = rank
        self.alpha = alpha
        self.scale = alpha / rank           # LoRA scaling factor

        # Frozen original weight
        self.weight = nn.Parameter(
            torch.empty(out_features, in_features), requires_grad=False)
        self.bias = nn.Parameter(
            torch.zeros(out_features), requires_grad=False)
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))

        # Trainable LoRA matrices
        self.lora_A = nn.Parameter(
            torch.randn(rank, in_features) * 0.01)   # init near 0
        self.lora_B = nn.Parameter(
            torch.zeros(out_features, rank))           # init to 0

        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        base   = x @ self.weight.T + self.bias          # frozen path
        lora   = self.dropout(x) @ self.lora_A.T @ self.lora_B.T
        return base + lora * self.scale

# Count parameters
base  = nn.Linear(4096, 4096)
lora  = LoRALinear(4096, 4096, rank=8)
print(f"Original params : {sum(p.numel() for p in base.parameters()):,}")
print(f"LoRA trainable  : {sum(p.numel() for p in lora.parameters() if p.requires_grad):,}")
# Original params : 16,781,312
# LoRA trainable  : 65,536   (~0.39%)
""")

story.append(h2("Using PEFT + TRL for LoRA Fine-tuning"))
story += code_block(
"""from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer

# 1 — Load base model (4-bit for memory efficiency)
from transformers import BitsAndBytesConfig
import torch

bnb = BitsAndBytesConfig(load_in_4bit=True,
                          bnb_4bit_compute_dtype=torch.bfloat16)
model_id = "meta-llama/Llama-3.2-3B-Instruct"
model    = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=bnb,
                                                 device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.pad_token = tokenizer.eos_token

# 2 — LoRA config
lora_cfg = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,                       # rank
    lora_alpha=32,              # alpha (scale = 32/16 = 2.0)
    target_modules=["q_proj","k_proj","v_proj","o_proj",
                    "gate_proj","up_proj","down_proj"],
    lora_dropout=0.05,
    bias="none",
)
model = get_peft_model(model, lora_cfg)
model.print_trainable_parameters()
# trainable params: 41,943,040 || all params: 3,254,964,224 || 1.29%

# 3 — Dataset (Alpaca format)
dataset = load_dataset("tatsu-lab/alpaca", split="train[:5000]")

def format_prompt(ex):
    if ex["input"]:
        return (f"### Instruction:\\n{ex['instruction']}\\n\\n"
                f"### Input:\\n{ex['input']}\\n\\n"
                f"### Response:\\n{ex['output']}")
    return (f"### Instruction:\\n{ex['instruction']}\\n\\n"
            f"### Response:\\n{ex['output']}")

# 4 — Training
args = TrainingArguments(
    output_dir="./lora-llama",
    num_train_epochs=2,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,   # effective batch = 16
    learning_rate=2e-4,
    warmup_ratio=0.05,
    lr_scheduler_type="cosine",
    fp16=True,
    logging_steps=10,
    save_strategy="epoch",
)
trainer = SFTTrainer(
    model=model, tokenizer=tokenizer,
    args=args, train_dataset=dataset,
    formatting_func=format_prompt,
    max_seq_length=1024,
)
trainer.train()
model.save_pretrained("./lora-adapter")
""")
story.append(sp(8))

story.append(h1("3.2  GRPO — Group Relative Policy Optimisation"))
story.append(p(
    "GRPO (used in DeepSeek-R1) is a simplified variant of PPO for training reasoning models. "
    "Instead of a learned value/critic network, it uses <b>group statistics</b>: "
    "generate G completions per prompt, compute reward for each, and use "
    "<i>normalised advantage = (r - mean(r)) / std(r)</i>."
))
story += code_block(
"""# Conceptual GRPO loop
import torch

def grpo_step(model, ref_model, tokenizer, prompts,
              reward_fn, G=8, beta=0.01, eps=0.2):
    \"\"\"
    prompts   : list of prompt strings
    reward_fn : callable(prompt, completion) -> float
    G         : group size (completions per prompt)
    beta      : KL penalty coefficient
    eps       : PPO clip epsilon
    \"\"\"
    all_advantages, all_log_probs, all_ref_log_probs = [], [], []

    for prompt in prompts:
        completions, rewards = [], []
        for _ in range(G):
            ids = model.generate(
                tokenizer(prompt, return_tensors="pt").input_ids.cuda(),
                max_new_tokens=256, do_sample=True, temperature=0.9)
            text = tokenizer.decode(ids[0], skip_special_tokens=True)
            completions.append(text)
            rewards.append(reward_fn(prompt, text))

        # Normalise within group → advantages
        rewards = torch.tensor(rewards)
        adv = (rewards - rewards.mean()) / (rewards.std() + 1e-8)

        for comp, a in zip(completions, adv):
            ids = tokenizer(prompt + comp, return_tensors="pt").input_ids.cuda()
            with torch.no_grad():
                lp_ref = compute_log_probs(ref_model, ids)
            lp_cur = compute_log_probs(model, ids)

            # Clipped surrogate + KL penalty
            ratio = torch.exp(lp_cur - lp_ref.detach())
            clipped = torch.clamp(ratio, 1-eps, 1+eps)
            pg_loss = -torch.min(ratio * a, clipped * a).mean()
            kl_pen  = beta * (lp_cur - lp_ref.detach()).mean()
            loss    = pg_loss + kl_pen
            loss.backward()

    return loss.item()

# Reward function example — format + correctness
def math_reward(prompt: str, completion: str) -> float:
    has_thinking = "<think>" in completion and "</think>" in completion
    # Check final answer against ground truth ...
    correct = check_answer(completion)  # your checker
    return (0.3 * has_thinking) + (1.0 * correct)
""")
story.append(note_box(
    "GRPO eliminates the critic network, halving memory compared to PPO. "
    "It's ideal for verifiable tasks: math, coding, logic puzzles where a reward function can "
    "score outputs automatically.", "tip"))
story.append(sp(8))

story.append(h1("3.3  Generating Custom Fine-Tuning Datasets"))
story += code_block(
"""import json
from openai import OpenAI
from pydantic import BaseModel
from typing import List
import instructor

client = instructor.from_openai(OpenAI())

class QAExample(BaseModel):
    instruction: str
    input: str
    output: str
    reasoning_trace: str   # chain-of-thought, stripped at training time if desired

SEED_TOPICS = [
    "explain gradient descent to a 10-year-old",
    "write a unit test for a binary search function",
    "debug this Python code: ...",
]

def generate_examples(topic: str, n: int = 5) -> List[QAExample]:
    return client.chat.completions.create(
        model="gpt-4o",
        response_model=List[QAExample],
        messages=[{
            "role": "system",
            "content": (
                "You are a dataset curator. Generate diverse, high-quality "
                f"training examples for the topic: {topic}. "
                "Vary difficulty, style, and length. Be accurate."
            )
        }],
        n=n
    )

# Build dataset
dataset = []
for topic in SEED_TOPICS:
    examples = generate_examples(topic, n=10)
    dataset.extend([ex.model_dump() for ex in examples])

# Save in JSONL (HuggingFace format)
with open("custom_dataset.jsonl", "w") as f:
    for ex in dataset:
        f.write(json.dumps(ex) + "\\n")

print(f"Generated {len(dataset)} examples")
""")
story.append(sp(8))

story.append(h1("3.4  SFT vs RFT — When to Use Each"))
story.append(h2("Supervised Fine-Tuning (SFT)"))
story += bul([
    "Train on (prompt, ideal_response) pairs with cross-entropy loss.",
    "Best for: style transfer, format adherence, domain knowledge injection.",
    "Requires: high-quality labeled data (quality >> quantity).",
    "Risk: model learns to <i>imitate</i> without truly reasoning.",
])
story.append(h2("Reinforcement Fine-Tuning (RFT / RLHF / GRPO)"))
story += bul([
    "Optimise a reward signal — human preferences (RLHF), verifiable answers (GRPO), or rule-based (RLAIF).",
    "Best for: reasoning, safety alignment, following complex instructions.",
    "Requires: a reliable reward model or verifiable task.",
    "Result: models that <i>generalise</i> to unseen problems.",
])
story.append(kv_table([
    ("Dimension", "SFT — RFT"),
    ("Data needed", "Labeled examples — Reward function / preference pairs"),
    ("Training cost", "Lower (1-3 epochs) — Higher (PPO/GRPO loop)"),
    ("Best for", "Format, style, domain — Reasoning, alignment"),
    ("Example use", "Customer service bot — Math reasoning, code correctness"),
    ("Overfitting risk", "High on small datasets — Lower (explores solutions)"),
]))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 4 — RAG SYSTEMS
# ════════════════════════════════════════════════════════════════════════════
story.append(section_banner("Part 4 — RAG Systems",
    "Retrieval-Augmented Generation for production knowledge systems"))
story.append(sp(12))

story.append(h1("4.1  8 RAG Architectures"))
story.append(h2("1. Naive RAG"))
story += code_block(
"""# Embed → Store → Retrieve → Generate
from sentence_transformers import SentenceTransformer
import faiss, numpy as np

embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Index
docs = ["Paris is the capital of France.", "Berlin is the capital of Germany."]
vecs = embedder.encode(docs, normalize_embeddings=True).astype("float32")
index = faiss.IndexFlatIP(vecs.shape[1])
index.add(vecs)

# Query
q = embedder.encode(["What is the capital of France?"],
                     normalize_embeddings=True).astype("float32")
D, I = index.search(q, k=2)
context = "\\n".join(docs[i] for i in I[0])
print(context)
""")

story.append(h2("2. Advanced RAG (re-ranking)"))
story += code_block(
"""from sentence_transformers import CrossEncoder

# After initial retrieval, re-rank with a cross-encoder
cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

query = "capital of France"
candidates = ["Paris is the capital.", "Lyon is a big city.",
              "France borders Spain.", "The Eiffel Tower is in Paris."]

scores = cross_encoder.predict([[query, c] for c in candidates])
ranked = sorted(zip(scores, candidates), reverse=True)
top_k  = [text for _, text in ranked[:2]]
""")

story.append(h2("3. Modular RAG – HyDE (Hypothetical Document Embedding)"))
story += code_block(
"""# Generate a hypothetical answer FIRST, embed it, then retrieve
# This bridges the query-document vocabulary gap

def hyde_retrieve(query: str, index, embedder, llm_client, k=5) -> list:
    # 1. Generate hypothetical answer
    hypo_doc = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":
            f"Write a short passage that would answer: {query}"}],
        max_tokens=150
    ).choices[0].message.content

    # 2. Embed the hypothetical doc (not the query)
    hypo_vec = embedder.encode([hypo_doc], normalize_embeddings=True)

    # 3. Retrieve against real corpus
    _, indices = index.search(hypo_vec.astype("float32"), k)
    return indices[0].tolist()
""")

story.append(h2("4–8. Additional Architectures Summary"))
story.append(kv_table([
    ("4. Self-RAG",        "Model decides WHEN to retrieve (special tokens: [Retrieve], [No Retrieve]). Reduces unnecessary lookups."),
    ("5. RAPTOR",          "Build a hierarchical tree by recursively summarising and clustering chunks. Enables multi-scale retrieval."),
    ("6. Graph RAG",       "Index knowledge as a graph (entities + relations). Query traverses edges for multi-hop reasoning."),
    ("7. Multi-vector RAG","Embed multiple representations per chunk (summary + propositions + full text). ColBERT-style late interaction."),
    ("8. Corrective RAG",  "Evaluate retrieved docs; if low quality, trigger web search as fallback. Self-corrects stale knowledge bases."),
]))
story.append(sp(8))

story.append(h1("4.2  Five Chunking Strategies"))
story += code_block(
"""from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)
from llama_index.core.node_parser import SentenceWindowNodeParser

# ─── 1. Fixed-size chunking ──────────────────────────────────────────────
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512, chunk_overlap=64,
    separators=["\\n\\n","\\n","."," ",""])

# ─── 2. Semantic chunking ────────────────────────────────────────────────
# Split on embedding similarity breakpoints (not fixed size)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

semantic = SemanticChunker(OpenAIEmbeddings(),
                            breakpoint_threshold_type="percentile",
                            breakpoint_threshold_amount=90)

# ─── 3. Document-structure aware (Markdown) ──────────────────────────────
md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#","H1"),("##","H2"),("###","H3")])
# Each chunk preserves its header hierarchy as metadata

# ─── 4. Sentence-window chunking ─────────────────────────────────────────
# Index single sentences but retrieve surrounding window for context
parser = SentenceWindowNodeParser.from_defaults(window_size=3)
# Retrieval returns the matched sentence + 3 sentences each side

# ─── 5. Proposition chunking ─────────────────────────────────────────────
# Decompose each chunk into atomic factual statements using an LLM
PROP_PROMPT = \"\"\"
Convert the following text into a list of atomic propositions
(one fact per line, self-contained):

{text}
\"\"\"
# Each proposition is indexed independently → high-precision retrieval
""")
story.append(sp(8))

story.append(h1("4.3  RAG vs Agentic RAG vs REFRAG"))
story.append(kv_table([
    ("RAG",          "Single-shot retrieval: query → retrieve → generate. Fast, cheap, good for well-structured corpora."),
    ("Agentic RAG",  "Multi-step: agent decides what to search, when, and how many times. Handles complex multi-hop questions. Uses ReAct loop."),
    ("REFRAG",       "REtrieval with Feedback: after generation, verify answer against sources; if grounding fails, re-retrieve with refined query."),
]))
story.append(sp(8))

story.append(h1("4.4  When to Choose Prompting vs RAG vs Fine-tuning"))
story.append(kv_table([
    ("Use Prompting when",    "Knowledge fits in context window, task is general, no private data needed, fast iteration required."),
    ("Use RAG when",          "Knowledge base is large or dynamic, private/proprietary documents, citations/grounding needed, knowledge changes frequently."),
    ("Use Fine-tuning when",  "Specific output style/format, domain-specific reasoning not in base model, latency critical (no retrieval step), behavior/personality change needed."),
    ("Use RAG + Fine-tune",   "Best of both: fine-tune for format/behavior, RAG for fresh knowledge. Used in most production enterprise systems."),
]))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 5 — CONTEXT ENGINEERING
# ════════════════════════════════════════════════════════════════════════════
story.append(section_banner("Part 5 — Context Engineering",
    "Designing the information landscape for AI agents"))
story.append(sp(12))

story.append(h1("5.1  6 Types of Context for AI Agents"))
story.append(kv_table([
    ("1. System context",   "Persona, capabilities, constraints, output format. Set in the system prompt. Rarely changes."),
    ("2. User context",     "Profile, preferences, subscription tier, locale. Fetched per user session."),
    ("3. Conversation context", "Full dialogue history (managed window). Essential for coherence across turns."),
    ("4. Task context",     "The current goal, intermediate steps, sub-task results. Grows as agent works."),
    ("5. Retrieved context","Documents/facts fetched from vector DB, web search, APIs. Just-in-time injection."),
    ("6. Tool context",     "Available tool definitions, recent tool outputs, error messages. Informs next action."),
]))
story.append(sp(8))

story.append(h1("5.2  Building Production Context Workflows"))
story += code_block(
"""from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import tiktoken

@dataclass
class ContextWindow:
    \"\"\"Manages the LLM context budget for a production agent.\"\"\"
    max_tokens: int = 128_000
    model: str = "gpt-4o"
    enc: any = field(init=False)

    def __post_init__(self):
        self.enc = tiktoken.encoding_for_model(self.model)

    def count(self, text: str) -> int:
        return len(self.enc.encode(text))

    def build_messages(
        self,
        system: str,
        history: List[Dict],
        retrieved_docs: List[str],
        user_message: str,
        reserve_for_output: int = 2000,
    ) -> List[Dict]:
        budget = self.max_tokens - reserve_for_output
        used   = self.count(system) + self.count(user_message)

        # 1 — Always include system
        messages = [{"role":"system","content":system}]

        # 2 — Add retrieved docs (highest priority after system)
        rag_block = ""
        for doc in retrieved_docs:
            candidate = f"\\n---\\n{doc}"
            if used + self.count(candidate) < budget * 0.4:  # max 40% for RAG
                rag_block += candidate
                used += self.count(candidate)

        if rag_block:
            messages.append({
                "role": "system",
                "content": f"Relevant documents:{rag_block}"
            })

        # 3 — Trim history from oldest, keeping most recent
        history_budget = budget - used
        trimmed = []
        for msg in reversed(history):
            tokens = self.count(msg["content"])
            if tokens <= history_budget:
                trimmed.insert(0, msg)
                history_budget -= tokens
            else:
                break   # drop oldest messages
        messages.extend(trimmed)

        # 4 — Current user message
        messages.append({"role":"user","content":user_message})
        return messages

# Usage
ctx = ContextWindow(max_tokens=128_000)
messages = ctx.build_messages(
    system="You are a helpful coding assistant...",
    history=[...],       # past turns
    retrieved_docs=["Python docs excerpt...", "Stack Overflow answer..."],
    user_message="How do I use asyncio.gather?",
)
""")
story.append(sp(8))

story.append(h1("5.3  Manual RAG vs Agentic Context Engineering"))
story.append(h2("Manual RAG"))
story += bul([
    "Fixed pipeline: query → embed → retrieve → inject → generate.",
    "Deterministic, auditable, fast.",
    "Fails on multi-hop questions requiring iterative refinement.",
])
story.append(h2("Agentic Context Engineering"))
story += bul([
    "Agent dynamically decides: what to retrieve, from which source, when to stop.",
    "Can call multiple tools, aggregate context, verify facts.",
    "Higher latency but handles ambiguous, complex queries.",
])
story += code_block(
"""# Agentic context loop
async def agentic_rag(question: str, tools, llm) -> str:
    context_store = []
    messages = [
        {"role":"system","content":
         "You are a research agent. Use tools to gather information, "
         "then synthesise a final answer. "
         "When you have enough context, output FINAL: <answer>"},
        {"role":"user","content":question}
    ]

    for step in range(10):   # max iterations
        response = await llm.chat(messages, tools=tools)
        messages.append({"role":"assistant","content":response.content})

        if response.content.startswith("FINAL:"):
            return response.content[6:].strip()

        if response.tool_calls:
            for call in response.tool_calls:
                result = await execute_tool(call.name, call.args)
                context_store.append(result)
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result)
                })

    return "Max iterations reached"
""")
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 6 — AI AGENTS
# ════════════════════════════════════════════════════════════════════════════
story.append(section_banner("Part 6 — AI Agents",
    "ReAct, agentic levels, multi-agent patterns, memory"))
story.append(sp(12))

story.append(h1("6.1  ReAct Pattern Implementation"))
story.append(p(
    "ReAct (Reasoning + Acting) interleaves natural language reasoning with tool calls, "
    "creating a transparent and controllable agent loop."
))
story += code_block(
"""import json
from openai import OpenAI

client = OpenAI()

# ─── Define tools ────────────────────────────────────────────────────────
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for current information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type":"string","description":"Search query"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type":"string","description":"Math expression"}
                },
                "required": ["expression"],
            },
        },
    },
]

def search_web(query: str) -> str:
    # In production: call SerpAPI, Tavily, etc.
    return f"[Mock search result for: {query}]"

def calculator(expression: str) -> str:
    try:
        return str(eval(expression, {"__builtins__":{}}, {}))
    except Exception as e:
        return f"Error: {e}"

TOOL_MAP = {"search_web": search_web, "calculator": calculator}

# ─── ReAct loop ──────────────────────────────────────────────────────────
def react_agent(user_query: str, max_steps: int = 10) -> str:
    messages = [
        {"role":"system","content":
         "You are a helpful agent. Reason carefully, use tools when needed, "
         "and give a final answer when you have enough information."},
        {"role":"user","content":user_query}
    ]

    for step in range(max_steps):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        messages.append(msg)

        if response.choices[0].finish_reason == "stop":
            return msg.content    # Final answer

        # Execute tool calls
        if msg.tool_calls:
            for tc in msg.tool_calls:
                fn_name = tc.function.name
                args    = json.loads(tc.function.arguments)
                result  = TOOL_MAP[fn_name](**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

    return "Max steps reached"

answer = react_agent(
    "What is the population of Tokyo multiplied by 0.035?")
print(answer)
""")
story.append(sp(8))

story.append(h1("6.2  5 Levels of Agentic AI Systems"))
story.append(kv_table([
    ("Level 1 – Chatbot",         "Stateless Q&A. No tools, no memory, no planning. Single LLM call."),
    ("Level 2 – Tool user",       "Can call external tools (search, calculator, API). Still single-turn or simple loops."),
    ("Level 3 – Multi-step agent","Plans across multiple steps. Maintains state within a session. ReAct loop."),
    ("Level 4 – Autonomous agent","Self-directs long-horizon tasks. Creates sub-goals, manages its own context window, recovers from errors."),
    ("Level 5 – Multi-agent system","Multiple specialised agents collaborate, delegate, and supervise each other. Supervisor + worker architecture."),
]))
story.append(sp(8))

story.append(h1("6.3  7 Multi-Agent System Patterns"))
story.append(kv_table([
    ("1. Supervisor / Worker",   "A coordinator agent decomposes tasks and delegates to specialised workers. Workers report back."),
    ("2. Peer-to-peer",          "Agents communicate directly (pub/sub or message passing). No central authority."),
    ("3. Pipeline",              "Sequential handoff: Agent A → Agent B → Agent C. Each transforms the artifact."),
    ("4. Parallel fan-out",      "Supervisor dispatches the same task to N agents in parallel, then merges results."),
    ("5. Debate / Critic",       "Generator agent produces output; Critic agent reviews; they iterate until consensus."),
    ("6. Memory-sharing",        "Agents share a common vector store or blackboard. Any agent can read/write knowledge."),
    ("7. Hierarchical tree",     "Agents organised in a tree. High-level agents plan; leaf agents execute. Used in large codebases."),
]))
story.append(sp(8))

story.append(h1("6.4  Agent2Agent (A2A) Protocol"))
story.append(p(
    "A2A is a Google-proposed open standard for agents to discover and communicate with "
    "other agents. Each agent exposes an <b>Agent Card</b> (JSON manifest) describing its "
    "capabilities, and communicates via a standardised message format over HTTP."
))
story += code_block(
"""# Agent Card (served at /.well-known/agent.json)
agent_card = {
    "name": "CodeReviewAgent",
    "description": "Reviews Python code for bugs and style issues",
    "version": "1.0",
    "skills": [
        {
            "id": "review_code",
            "name": "Review Code",
            "description": "Review Python code and return structured feedback",
            "inputModes":  ["text"],
            "outputModes": ["text"],
        }
    ],
    "endpoint": "https://myagent.example.com/a2a",
    "authentication": {"schemes": ["Bearer"]},
}

# Sending a task to another agent (A2A task format)
import httpx, uuid

async def call_remote_agent(agent_url: str, skill_id: str,
                             message: str, token: str) -> str:
    task = {
        "id": str(uuid.uuid4()),
        "message": {
            "role": "user",
            "parts": [{"type": "text", "text": message}]
        }
    }
    resp = await httpx.AsyncClient().post(
        agent_url,
        json=task,
        headers={"Authorization": f"Bearer {token}"},
    )
    result = resp.json()
    return result["artifact"]["parts"][0]["text"]
""")
story.append(sp(8))

story.append(h1("6.5  Memory Types and Management"))
story.append(kv_table([
    ("In-context (working)",  "The active messages list. Fastest, but limited by context window. Evict old messages with summarisation."),
    ("External episodic",     "Vector DB storing past conversations as embeddings. Retrieve relevant episodes by similarity."),
    ("External semantic",     "Structured knowledge base (facts, entities). Retrieved via search or graph traversal."),
    ("Procedural (weights)",  "Fine-tuned knowledge baked into model weights. Permanent but requires retraining to update."),
    ("Cache",                 "KV-cache for repeated prefixes. Reduces latency on long system prompts."),
]))
story += code_block(
"""# Episodic memory with summarisation
from openai import OpenAI
from datetime import datetime

client = OpenAI()

class AgentMemory:
    def __init__(self, max_messages=20, summary_threshold=15):
        self.messages   = []
        self.summaries  = []
        self.max_msgs   = max_messages
        self.threshold  = summary_threshold

    def add(self, role: str, content: str):
        self.messages.append({
            "role":role,"content":content,
            "timestamp": datetime.utcnow().isoformat()
        })
        if len(self.messages) >= self.threshold:
            self._compress()

    def _compress(self):
        \"\"\"Summarise oldest half of messages.\"\"\"
        to_compress = self.messages[:self.threshold//2]
        self.messages = self.messages[self.threshold//2:]
        block = "\\n".join(f"{m['role']}: {m['content']}" for m in to_compress)
        summary = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":
                       f"Summarise this conversation excerpt in 3 sentences:\\n{block}"}],
            max_tokens=200,
        ).choices[0].message.content
        self.summaries.append(summary)

    def get_context(self) -> list:
        ctx = []
        if self.summaries:
            ctx.append({"role":"system",
                        "content":"Previous conversation summary:\\n"+
                        "\\n".join(self.summaries)})
        ctx.extend(self.messages)
        return ctx
""")
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 7 — MCP PROTOCOL
# ════════════════════════════════════════════════════════════════════════════
story.append(section_banner("Part 7 — MCP Protocol",
    "Model Context Protocol — the USB-C for AI tools"))
story.append(sp(12))

story.append(h1("7.1  MCP Fundamentals"))
story.append(p(
    "The <b>Model Context Protocol</b> (Anthropic, 2024) is a standardised protocol "
    "for connecting LLMs to external tools, data sources, and services. "
    "It defines a client-server architecture where the AI application is the <b>host</b>, "
    "MCP servers expose capabilities, and the LLM is the <b>client</b> consuming them."
))
story += bul([
    "<b>Resources</b> – Expose data (files, DB rows, API responses) as readable context.",
    "<b>Tools</b> – Functions the model can call (search, execute code, send email).",
    "<b>Prompts</b> – Reusable prompt templates with parameters.",
    "<b>Sampling</b> – Server-side requests for the model to generate text.",
])
story.append(sp(8))

story.append(h1("7.2  MCP vs APIs vs Function Calling"))
story.append(kv_table([
    ("REST APIs",         "Static, require custom integration per API. No standard for discovery or capability description."),
    ("Function Calling",  "OpenAI-specific. JSON schema definitions inline in the prompt. Works, but vendor-locked and not composable."),
    ("MCP",               "Vendor-neutral, standardised, discoverable. Servers can be shared across any MCP-compatible host. Like OpenAPI but for AI tools."),
]))
story.append(sp(8))

story.append(h1("7.3  Building MCP Clients and Servers"))
story.append(h2("MCP Server (Python)"))
story += code_block(
"""from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import httpx

app = Server("weather-server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_weather",
            description="Get current weather for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type":"string","description":"City name"},
                    "units": {"type":"string","enum":["metric","imperial"],
                              "default":"metric"},
                },
                "required": ["city"],
            }
        ),
        types.Tool(
            name="get_forecast",
            description="Get 5-day weather forecast",
            inputSchema={
                "type": "object",
                "properties": {
                    "city":{"type":"string"},
                    "days":{"type":"integer","minimum":1,"maximum":5}
                },
                "required": ["city"],
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_weather":
        city  = arguments["city"]
        units = arguments.get("units","metric")
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q":city,"units":units,"appid":"YOUR_API_KEY"})
        data = resp.json()
        return [types.TextContent(
            type="text",
            text=f"Weather in {city}: {data['weather'][0]['description']}, "
                 f"{data['main']['temp']}°{'C' if units=='metric' else 'F'}"
        )]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream,
                      app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
""")

story.append(h2("MCP Client (connecting to a server)"))
story += code_block(
"""from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_mcp_server():
    server_params = StdioServerParameters(
        command="python",
        args=["weather_server.py"],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover available tools
            tools = await session.list_tools()
            print([t.name for t in tools.tools])

            # Call a tool
            result = await session.call_tool(
                "get_weather",
                arguments={"city":"Tokyo","units":"metric"}
            )
            print(result.content[0].text)
            # Weather in Tokyo: light rain, 18°C
""")
story.append(sp(8))

story.append(h1("7.4  Avoiding Tool Overload"))
story.append(p(
    "Providing too many tools degrades LLM performance. "
    "Studies show accuracy drops sharply after ~10–15 tools in context. "
    "Strategies to manage tool proliferation:"
))
story += bul([
    "<b>Tool routing</b> – A small classifier or LLM call selects the relevant subset of tools before the main agent call.",
    "<b>Hierarchical tools</b> – Group related tools behind a single meta-tool (e.g. <i>database_tool</i> with a sub-command parameter).",
    "<b>Tool descriptions matter</b> – Clear, concise, distinct descriptions reduce the model's selection confusion.",
    "<b>Dynamic tool loading</b> – Load tools based on conversation topic detected from recent messages.",
    "<b>Benchmark</b> – Test accuracy with 5, 10, 20, 50 tools using your eval suite; find the sweet spot.",
])
story += code_block(
"""# Tool routing — inject only relevant tools
from openai import OpenAI

ALL_TOOLS = {
    "weather": [...weather_tools...],
    "calendar": [...calendar_tools...],
    "email":    [...email_tools...],
    "code":     [...code_tools...],
}

def route_tools(user_message: str) -> list:
    \"\"\"Classify the request and return only relevant tools.\"\"\"
    routing_resp = OpenAI().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role":"user",
            "content": (
                f"Categories: {list(ALL_TOOLS.keys())}\\n"
                f"Message: {user_message}\\n"
                "Which categories are relevant? Reply with JSON list."
            )
        }],
        response_format={"type":"json_object"}
    )
    import json
    cats = json.loads(routing_resp.choices[0].message.content)
    tools = []
    for cat in cats.get("categories",[]):
        tools.extend(ALL_TOOLS.get(cat,[]))
    return tools[:12]   # hard cap
""")
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# PART 8 — PRODUCTION & DEPLOYMENT
# ════════════════════════════════════════════════════════════════════════════
story.append(section_banner("Part 8 — Production & Deployment",
    "Model compression, serving, evaluation, and observability"))
story.append(sp(12))

story.append(h1("8.1  Model Compression Techniques"))
story.append(kv_table([
    ("Quantisation",    "Reduce weight precision: FP32→FP16→INT8→INT4. 4-bit (GPTQ, AWQ, NF4) gives ~4x size reduction with minimal quality loss."),
    ("Pruning",         "Remove weights near zero. Structured pruning removes entire heads/layers. Unstructured requires sparse hardware to benefit."),
    ("Knowledge Distillation","Train a small student model to mimic a large teacher's logits. Used to create Phi, DistilBERT, etc."),
    ("GPTQ",            "Post-training quantisation with layer-wise second-order optimisation. Best accuracy among PTQ methods."),
    ("AWQ",             "Activation-aware quantisation. Protects salient weights based on activation magnitude. Faster inference than GPTQ."),
]))
story += code_block(
"""# AWQ quantisation with AutoAWQ
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

model_id = "meta-llama/Llama-3.2-7B-Instruct"
quant_path = "./llama-3.2-7b-awq"

model     = AutoAWQForCausalLM.from_pretrained(model_id, device_map="auto")
tokenizer = AutoTokenizer.from_pretrained(model_id)

quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,              # 4-bit weights
    "version": "GEMM"        # fast kernel
}
model.quantize(tokenizer, quant_config=quant_config)
model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)
# Model goes from ~14 GB → ~3.5 GB
""")
story.append(sp(8))

story.append(h1("8.2  KV Caching in LLMs"))
story.append(p(
    "During autoregressive generation, the model recomputes key/value matrices for all "
    "previous tokens at every step — O(n²) cost. <b>KV caching</b> stores these matrices "
    "in GPU memory and reuses them, reducing generation to O(n) per new token."
))
story += code_block(
"""# Transformers KV cache (automatic)
from transformers import AutoModelForCausalLM, AutoTokenizer, DynamicCache
import torch

model_id = "meta-llama/Llama-3.2-1B"
model     = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16).cuda()
tokenizer = AutoTokenizer.from_pretrained(model_id)

# Long shared prefix (system prompt) — compute once
system = "You are a Python expert. " * 100   # 500 tokens
inputs  = tokenizer(system, return_tensors="pt").input_ids.cuda()

# Build the prefix KV cache
with torch.no_grad():
    prefix_cache = DynamicCache()
    out = model(inputs, past_key_values=prefix_cache, use_cache=True)
    prefix_cache = out.past_key_values   # saved keys/values

# Now answer multiple queries reusing the prefix cache
for query in ["What is a generator?", "Explain decorators."]:
    q_ids = tokenizer(query, return_tensors="pt").input_ids.cuda()
    # Reuse cached prefix — only compute Q tokens
    with torch.no_grad():
        gen = model.generate(
            q_ids,
            past_key_values=prefix_cache,
            max_new_tokens=100,
            use_cache=True,
        )
    print(tokenizer.decode(gen[0][q_ids.shape[-1]:], skip_special_tokens=True))
""")
story.append(note_box(
    "Prefix caching (vLLM, SGLang) hashes and reuses KV blocks for identical prompt prefixes "
    "across requests. This is a 2-10x throughput win for applications with long shared system prompts.", "tip"))
story.append(sp(8))

story.append(h1("8.3  Multi-turn Evaluations"))
story += code_block(
"""# Evaluate agent over a trajectory (not single response)
from dataclasses import dataclass
from typing import List, Callable
import json

@dataclass
class Turn:
    user:      str
    assistant: str
    expected:  str | None = None

@dataclass
class Conversation:
    id:    str
    turns: List[Turn]
    final_goal: str       # what the full conversation should achieve

# ─── Metrics ─────────────────────────────────────────────────────────────
def coherence_score(history: List[Turn], llm) -> float:
    \"\"\"Ask an LLM to rate conversation coherence 0-10.\"\"\"
    convo = "\\n".join(f"U:{t.user}\\nA:{t.assistant}" for t in history)
    resp = llm.chat([{"role":"user","content":
        f"Rate coherence 0-10 (JSON: {{\\\"score\\\": N}}):\\n{convo}"}])
    return json.loads(resp)["score"] / 10

def goal_completion(convo: Conversation, llm) -> float:
    \"\"\"Did the agent achieve the final goal?\"\"\"
    history = "\\n".join(f"U:{t.user}\\nA:{t.assistant}" for t in convo.turns)
    resp = llm.chat([{"role":"user","content":
        f"Goal: {convo.final_goal}\\n\\nConversation:\\n{history}\\n\\n"
        "Was the goal achieved? JSON: {\\\"achieved\\\": true/false, \\\"score\\\": 0-1}"}])
    return json.loads(resp)["score"]

def turn_accuracy(turns: List[Turn]) -> float:
    \"\"\"Exact-match accuracy where expected responses are specified.\"\"\"
    scored = [t for t in turns if t.expected]
    if not scored: return 1.0
    return sum(1 for t in scored
               if t.expected.strip().lower() in t.assistant.lower()) / len(scored)

# ─── Run evaluation suite ─────────────────────────────────────────────────
def evaluate_agent(agent_fn: Callable, test_cases: List[Conversation]) -> dict:
    results = []
    for case in test_cases:
        history = []
        turns   = []
        for turn in case.turns:
            response = agent_fn(turn.user, history)
            history.append({"role":"user","content":turn.user})
            history.append({"role":"assistant","content":response})
            turns.append(Turn(turn.user, response, turn.expected))

        results.append({
            "id":       case.id,
            "accuracy": turn_accuracy(turns),
        })
    avg = sum(r["accuracy"] for r in results) / len(results)
    return {"mean_accuracy": avg, "details": results}
""")
story.append(sp(8))

story.append(h1("8.4  vLLM and LitServe for Inference"))
story.append(h2("vLLM — High-throughput serving with PagedAttention"))
story += code_block(
"""pip install vllm
""", "Shell")
story += code_block(
"""# Start vLLM server (OpenAI-compatible)
python -m vllm.entrypoints.openai.api_server \\
    --model meta-llama/Llama-3.1-8B-Instruct \\
    --quantization awq \\
    --tensor-parallel-size 2 \\         # split across 2 GPUs
    --max-model-len 32768 \\
    --enable-prefix-caching \\
    --port 8000
""", "Shell")
story += code_block(
"""# Query vLLM just like OpenAI API
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")
resp = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role":"user","content":"Explain vLLM PagedAttention"}],
    temperature=0.3,
    max_tokens=500,
)
print(resp.choices[0].message.content)

# Batch inference (offline)
from vllm import LLM, SamplingParams

llm = LLM(model="meta-llama/Llama-3.2-3B", gpu_memory_utilization=0.85)
params = SamplingParams(temperature=0.7, top_p=0.9, max_tokens=200)
prompts = ["Explain transformers", "What is RLHF?", "Define attention mechanism"]
outputs = llm.generate(prompts, params)
for o in outputs:
    print(o.outputs[0].text)
""")

story.append(h2("LitServe — Fast API for ML models"))
story += code_block(
"""from litserve import LitAPI, LitServer
from transformers import pipeline

class LLMApi(LitAPI):
    def setup(self, device):
        self.pipe = pipeline(
            "text-generation",
            model="meta-llama/Llama-3.2-1B-Instruct",
            device=device,
            torch_dtype="auto"
        )

    def decode_request(self, request):
        return request["prompt"]

    def predict(self, prompt):
        result = self.pipe(prompt, max_new_tokens=200, temperature=0.7)
        return result[0]["generated_text"]

    def encode_response(self, output):
        return {"generated_text": output}

if __name__ == "__main__":
    api    = LLMApi()
    server = LitServer(api,
                       accelerator="gpu",
                       devices=1,
                       workers_per_device=2,   # 2 workers per GPU
                       max_batch_size=16,       # dynamic batching
                       batch_timeout=0.05)
    server.run(port=8080)
""")
story.append(sp(8))

story.append(h1("8.5  LLM Observability Strategies"))
story.append(p(
    "Monitoring LLM applications requires tracking more than latency and errors. "
    "You need to understand <i>what</i> the model is doing and <i>why</i>."
))
story.append(kv_table([
    ("Tracing",         "Record full input/output/latency for every LLM call. Use OpenTelemetry or LangSmith/Langfuse."),
    ("Cost tracking",   "Token counts × price per token per model. Alert on anomalies (prompt injection can inflate tokens)."),
    ("Quality metrics", "Automated scoring: faithfulness (RAG), relevance, toxicity, PII detection on every response."),
    ("User feedback",   "Thumbs up/down, ratings, corrections. Connect to a retraining pipeline."),
    ("Drift detection", "Monitor response distributions over time. Topic drift, length drift, refusal rate changes signal issues."),
    ("Prompt versioning","Track which prompt version produced which outputs. A/B test prompts like software features."),
]))
story += code_block(
"""# Langfuse tracing (open-source observability)
from langfuse import Langfuse
from langfuse.openai import openai   # patched openai client
import os

langfuse = Langfuse(
    public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
    secret_key=os.environ["LANGFUSE_SECRET_KEY"],
    host="https://cloud.langfuse.com"
)

# All OpenAI calls now auto-traced
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role":"user","content":"Hello"}],
    # Optional metadata
    metadata={"user_id":"u123","session":"s456","version":"v2.1"},
)

# Manual scoring (e.g. from user feedback)
trace_id = response._raw_response.headers.get("x-langfuse-trace-id")
langfuse.score(
    trace_id=trace_id,
    name="user_feedback",
    value=1.0,   # thumbs up
    comment="Very helpful response"
)

# Custom evaluation score
from langfuse import Langfuse
lf = Langfuse()
lf.score(
    trace_id=trace_id,
    name="faithfulness",
    value=0.92,
    data_type="NUMERIC"
)
""")
story.append(sp(12))

# ── Closing ───────────────────────────────────────────────────────────────────
story.append(hr())
story.append(Paragraph("You've reached the end of the LLM Engineering Complete Guide.",
    S("_end1", fontSize=12, leading=18, fontName="Helvetica-Bold",
      textColor=C_ACCENT, alignment=TA_CENTER, spaceBefore=12)))
story.append(Paragraph(
    "Keep building. Keep experimenting. The field moves fast — "
    "but these fundamentals compound.",
    S("_end2", fontSize=10, leading=16, fontName="Helvetica-Oblique",
      textColor=C_MUTED, alignment=TA_CENTER, spaceAfter=8)))
story.append(hr())

# ════════════════════════════════════════════════════════════════════════════
# BUILD
# ════════════════════════════════════════════════════════════════════════════
doc.build(story)
print(f"PDF written to {OUTPUT}")

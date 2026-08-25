<div align="center">

# 🧠 PaperMind AI
### *Autonomous Research Paper Comprehension, First-Principles Synthesis & Interactive Tutor Engine*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=flat&logo=python)](https://python.org)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-FF6F00.svg?style=flat)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/Groq-LPU_Fast_Inference-F55036.svg?style=flat)](https://groq.com)
[![arXiv](https://img.shields.io/badge/arXiv-API-B31B1B.svg?style=flat)](https://arxiv.org)
[![License](https://img.shields.io/badge/License-Proprietary_Source--Available-red.svg?style=flat)](LICENSE)
[![Contributions](https://img.shields.io/badge/Contributions-Closed-orange.svg?style=flat)](CONTRIBUTING.md)
[![Status](https://img.shields.io/badge/Version-1.0.0--Stable-brightgreen.svg?style=flat)](#-version-20-roadmap--upcoming-speed-upgrades)

</div>

---

## 📖 Overview

**PaperMind AI** is an autonomous research paper intelligence agent designed to make cutting-edge AI and scientific literature instantly comprehensible. Powered by a cyclic **LangGraph state machine**, it ingests any arXiv paper URL or uploaded PDF, breaks down complex algorithms into **first-principles intuitions using the Feynman technique**, self-evaluates comprehension with **automated recall quizzes (with an automatic retry feedback loop)**, and produces clean **PyTorch/Python reference implementations** alongside peer-level teach-back summaries.

---

## ⚡ The Agentic Feedback Pipeline

Unlike simple one-shot LLM wrappers, **PaperMind AI** uses a self-correcting cyclic graph to ensure genuine understanding before output generation:

```
┌──────────────┐     ┌────────────────┐     ┌──────────────────┐
│ Ingest Node  │ ──► │ Understand     │ ──► │ Recall Check     │
│ (arXiv/PDF)  │     │ (Feynman Stack)│     │ (Quiz & Scoring) │
└──────────────┘     └────────────────┘     └─────────┬────────┘
                            ▲                         │
                            │   Score < 0.7 & Retries │
                            └─── [Feedback Loop] ◄────┤
                                                      │ Score >= 0.7
                                                      ▼
                                            ┌──────────────────┐
                                            │ Apply Node       │ ──► [END / JSON API]
                                            │ (PyTorch + Teach)│
                                            └──────────────────┘
```

1. **Ingest Node**: Dual-mode ingestion supporting direct arXiv URL/ID parsing and local PDF uploads with section extraction (Abstract, Introduction, Method/Architecture, Conclusion).
2. **Understand Node**: De-jargonizes the paper into fundamental truths and smart-novice analogies. If triggered via a retry, it dynamically incorporates specific feedback from failed quizzes.
3. **Recall Check Node**: Generates conceptual self-assessment questions and evaluates understanding depth on a `0.0` to `1.0` scale.
4. **Conditional Router**: If `score < 0.7` and `attempt < 3`, routes back to `understand` with targeted review feedback; otherwise proceeds to `apply`.
5. **Apply Node**: Synthesizes a clean, runnable Python/PyTorch code sketch from scratch and writes a 3–5 sentence peer teach-back summary.

---

## 🚀 Multi-Provider LLM Support (Groq Free Tier Default)

PaperMind AI is optimized for fast inference across major LLM providers:

* ⚡ **Groq (Recommended Free Tier)**: `openai/gpt-oss-120b` (120B parameter model), `openai/gpt-oss-20b`, `qwen/qwen3.6-27b`, `mixtral-8x7b-32768`.
* 💎 **Google Gemini (Free Tier)**: `gemini-2.0-flash`, `gemini-1.5-flash`.
* 🧠 **Anthropic Claude**: `claude-3-7-sonnet-20250219`, `claude-3-5-sonnet-20241022`.
* 🤖 **OpenAI**: `gpt-4o`, `gpt-4o-mini`.

---

## 🖥️ Interactive Web Dashboard

Launch the built-in dark mode web UI:

```bash
python app.py
```
Open **`http://localhost:5007`** in your browser to access:

* 🌐 **arXiv URL Explorer**: Ingest papers by ID or full URL with 1-click presets (*Attention, LoRA, DDPM, FlashAttention*).
* 📄 **Drag-and-Drop PDF Upload**: Directly upload any local research paper PDF for instant breakdown.
* 📊 **Live Visual Pipeline Tracker**: Real-time multi-stage status indicator showing ingestion, understanding, quiz scoring, and code generation.
* 📖 **First-Principles Tab**: Markdown-formatted Feynman breakdown.
* 🎯 **Recall Quiz Tab**: Interactive questions with toggleable answer reveals and evaluator feedback.
* 💻 **Code & Teach-Back Tab**: Syntax-highlighted PyTorch reference code with 1-click clipboard copy.
* 📑 **Extracted Sections Tab**: Collapsible view of raw parsed paper sections.

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/papermind-ai.git
cd papermind-ai
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
```
Edit `.env` and add your free Groq API key from [console.groq.com](https://console.groq.com):
```env
LLM_PROVIDER=groq
GROQ_API_KEY="gsk_your_api_key_here"
MODEL_NAME=openai/gpt-oss-120b
PORT=5007
RECALL_PASS_THRESHOLD=0.7
MAX_RETRIES=3
```

---

## 💻 Running the Application

### Start the Web UI & API Server
```bash
python app.py
```
Visit: **`http://localhost:5007`**

### Or use the REST API via `curl`

**Analyze via arXiv URL/ID:**
```bash
curl -X POST http://localhost:5007/analyze \
  -H "Content-Type: application/json" \
  -d '{"paper_url": "https://arxiv.org/abs/1706.03762"}'
```

**Analyze via Local PDF Upload:**
```bash
curl -X POST http://localhost:5007/analyze \
  -F "file=@/path/to/paper.pdf"
```

**Check Service Health:**
```bash
curl http://localhost:5007/health
```

---

## 🧪 Testing Suite

PaperMind AI includes comprehensive unit and integration mock tests covering URL normalization, text cleaning, JSON evaluation parsing, conditional routing, multi-step retry loops, and direct PDF uploads.

Run all tests:
```bash
pytest -v
```

---

## 📁 Repository Structure

```
papermind-ai/
├── app.py                  # Flask API server & UI router (/health, /analyze)
├── config.py               # Provider settings, model defaults, hyperparameters
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Core dependencies
├── LICENSE                 # Proprietary source-available license
├── CONTRIBUTING.md         # Contribution policy (external PRs closed)
├── SECURITY.md             # Security reporting policy
├── graph/                  # LangGraph Agent Core
│   ├── state.py            # AgentState TypedDict
│   ├── builder.py          # StateGraph wiring and conditional routing
│   ├── llm.py              # Multi-provider LLM factory & tag cleaner
│   └── nodes/
│       ├── ingest.py       # PDF download / upload & text extraction
│       ├── understand.py   # Feynman first-principles breakdown
│       ├── recall_check.py # Self-scoring quiz evaluation
│       └── apply.py        # Code sketch & teach-back generator
├── tools/                  # PDF & arXiv Utilities
│   ├── arxiv_fetcher.py    # URL normalization and HTTP fetcher
│   └── pdf_parser.py       # PDF reader and section detector
├── prompts/                # Prompt Templates
│   ├── understand.txt      # First-principles prompt
│   ├── recall_quiz.txt     # Quiz evaluation prompt
│   └── teach_back.txt      # Code synthesis & teach-back prompt
├── templates/
│   └── index.html          # Modern dark-mode Web UI
└── tests/
    └── test_graph.py       # 8 unit & integration mock tests
```

---

## 🚀 Version 2.0 Roadmap & Upcoming Technical Upgrades

The upcoming **v2.0 release** transforms PaperMind AI into an enterprise-grade, sub-second research intelligence platform through native systems programming, speculative execution, and enhanced cognitive workflows:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PAPERMIND AI — VERSION 2.0 ARCHITECTURE                         │
├──────────────────────────────┬─────────────────────────────┬───────────────────────────┤
│    🦀 RUST CORE ENGINE       │   ⚡ STREAMING PIPELINE     │   🧠 COGNITIVE & STUDY    │
│  • PyO3 / C-Bindings         │ • Sub-second SSE Streaming  │ • 8-Layer Bloom Stack     │
│  • SIMD PDF Layout Parsing   │ • Speculative 2-Tier Engine │ • Anki .apkg / CSV Export │
│  • Rust-Native Tokenizer     │ • WebSockets State Updates  │ • Obsidian [[WikiLinks]]  │
│  • Zero-Copy mmap Buffering  │ • Chunked LPU Token Feeds   │ • HNSW Vector RAG Chat    │
└──────────────────────────────┴─────────────────────────────┴───────────────────────────┘
```

### 1. 🦀 Native Rust Core & C-Engine Acceleration (`PyO3`)
* **SIMD-Accelerated PDF Ingestion**: Replacing pure-Python PDF parsers with a native **Rust engine (`pdf-extract-rs` / PyO3 / PyMuPDF C-bindings)**, achieving **15x–30x faster text extraction** (<15ms per 20-page paper).
* **Multi-Column Column Reflow & De-noising**: Native geometric bounding-box sorting to reconstruct complex multi-column academic layouts without corrupting mathematical equations or footnotes.
* **Zero-Copy Memory-Mapped Buffers (`mmap`)**: Stream PDF bytes directly from network sockets into native memory without intermediate Python string allocation overhead.
* **Rust-Native Token Counter**: High-speed BPE tokenization in Rust for precise context-window budgeting before dispatching to LLM providers.

### 2. ⚡ Real-Time Token Streaming & Sub-Second TTFT
* **Server-Sent Events (SSE) & WebSockets**: Transition from batch REST responses to live chunked streaming over SSE, providing **Time-To-First-Token (TTFT) under 400ms**.
* **Progressive Markdown & Math Rendering**: Stream First-Principles notes and PyTorch code blocks progressively into the UI in real-time as Groq LPUs generate tokens.
* **Live Graph Node State Broadcasting**: Real-time visual progress indicators highlighting the active LangGraph node (`Ingest` ➔ `Understand` ➔ `Recall Check` ➔ `Apply`).

### 3. 🌊 Speculative Two-Tier Cognitive Synthesis
* **Tier 1 — Instant Executive Skim (<1.2s)**: Speculative first-pass summary (Core Problem, Proposed Architecture, Primary Benchmark Result) generated instantly via lightweight 20B models (`openai/gpt-oss-20b`).
* **Tier 2 — Asynchronous Deep-Stack Decomposition**: Concurrent background extraction of first-principles axioms, Socratic 5-Whys causal analysis, and runnable PyTorch code via 120B parameter models.

### 4. 🎴 Active Recall & Spaced Repetition (Anki Deck Export)
* **Automated Cloze & QA Flashcard Generation**: Extract high-yield conceptual flashcards formatted with LaTeX math and code snippets.
* **Direct Export to Anki (`.apkg` and `.csv`)**: One-click export into Anki desktop/mobile with hierarchical paper tags (`#paper/attention`, `#ml/transformers`).
* **In-App 3D Flip Study Player**: Interactive review session directly inside the web UI powered by an embedded SM-2 / Leitner spaced repetition scheduler.

### 5. 🕸️ Embedded Vector Memory & Knowledge Graph (RAG)
* **Cross-Paper Vector Search**: Embedded Rust-based HNSW vector index (Qdrant/Faiss) for asking grounded technical questions across your entire paper collection.
* **Obsidian-Compatible Vault Generation**: Auto-generate markdown notes with YAML frontmatter, math blocks, and bidirectional `[[WikiLinks]]` connecting papers to foundational concepts.
* **Interactive Force-Directed Graph (D3.js / WebGL)**: Visual 3D concept graph linking papers, architectures, mathematical axioms, and shared benchmarks.

### 6. 🎨 Advanced UI / UX & Math Typography
* **KaTeX / LaTeX Mathematical Typesetting**: Full textbook-grade rendering of complex loss functions, matrix equations, and mathematical derivations.
* **Monaco / CodeMirror Interactive Editor**: Live editable code sketch sandbox with syntax highlighting and instant snippet execution.
* **Zero-Build Vanilla Architecture**: Ultra-lightweight, responsive dark-mode dashboard with zero heavy build tool dependencies.


---

## 🔒 License & Contribution Policy

### License
Copyright (c) 2025–2026 Dhruv Sharma. All Rights Reserved.  
This project is licensed under a proprietary and source-available license for personal, non-commercial, and academic evaluation purposes. See [LICENSE](LICENSE) for details.

### Notice on Contributions
**External contributions and pull requests are strictly closed.** Please review [CONTRIBUTING.md](CONTRIBUTING.md) for further information. Bug reports and feature discussions can be submitted via the [Issues](../../issues) tab.

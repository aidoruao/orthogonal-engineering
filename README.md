# Orthogonal Engineering for LLMs

**A constraint-first methodology for extracting reliable outputs from unreliable AI systems.**

Instead of fighting LLM verbosity, hallucination, and drift—design systems that **channel noise into signal**.

---

## 🔗 Live Demos

- **[Full Guide & Interactive Demo](https://yourusername.github.io/orthogonal-engineering/)** - Complete methodology with live extraction tool
- **[Theory Paper (v3)](https://yourusername.github.io/orthogonal-engineering/theory/)** - Structural analysis and formal definitions
- **[Workbench Tool (v4)](https://yourusername.github.io/orthogonal-engineering/workbench/)** - Minimal interactive invariant extractor

---

## 💡 Core Concept

**Traditional Approach:**
- Try to make LLMs more "reliable"
- Fight against verbosity and drift
- Hope for perfect outputs

**Orthogonal Engineering:**
- Accept LLM constraints as structural facts
- Design prompts that **route** slack into canals
- Extract invariants from predictable noise patterns
- Treat verbosity as **energy to be channeled**, not a bug to fix

---

## 🏗️ The Four Layers

### Layer 1: Benevolent Absence
The LLM cannot give you what you want **in the form you want**, but it **can** give you something extractable embedded in drift.

### Layer 2: Structural Extraction
Use **post-processing**, **timing analysis**, **templates**, or **forced structure** to pull the invariant from the output.

### Layer 3: Raised Fields (Templates & Canals)
Design prompts as **constraint channels** that localize drift into designated slots while keeping the core answer clean.

### Layer 4: Iterative Refinement
Use extracted invariants as seeds for progressively more constrained queries. Each iteration collapses more slack.

---

## 🛠️ Ready-Made Canal Kits

The repository includes working templates for:
- **Enum Extraction** (sentiment, classification)
- **Date/Time Extraction** (events, scheduling)
- **SQL Query Extraction** (with safety validation)
- **Structured JSON Outputs** (Pydantic models)

---

## 📊 Validated Use Cases

- **Chat Export Analysis**: Normalized 3,842+ messages from ChatGPT/Claude exports
- **DSCA (Deep Spiritual Conversation Analysis)**: Timing bursts, turn-taking patterns
- **LLM API Controllers**: Violation logging, invariant extraction from verbose outputs
- **Conversation Archaeology**: Extracting signal from 600+ AI conversation archives

---

## 🧬 Methodology

> "Don't fight the current—build canals so the current turns your mill."

You are **not** fixing the model. You are **engineering around its nature** by:

1. **Designing prompts that anticipate and route slack**
2. **Using iterative refinement to collapse noise progressively**
3. **Separating invariant extraction from generative acts**
4. **Treating LLM verbosity as a predictable force to be channeled**

---

## 🎯 Key Principles

- **Benevolent Absence**: The system can't deliver what you want, but *can* deliver an extractable approximation
- **Invariant**: A property that remains stable under constraint-induced drift
- **Canal Architecture**: Structural pathways that divert entropy away from the analysis layer
- **Orthogonality**: Work perpendicular to the constrained axis rather than against it

---

## 📖 Project Structure

```
orthogonal-engineering/
├── index.html              # Main guide with interactive demo
├── theory/
│   └── index.html         # Formal structural document (v3)
├── workbench/
│   └── index.html         # Minimal extraction tool (v4)
└── README.md              # This file
```

---

## 🚀 Quick Start

1. **Read the [Full Guide](https://yourusername.github.io/orthogonal-engineering/)** for methodology and examples
2. **Try the [Workbench Tool](https://yourusername.github.io/orthogonal-engineering/workbench/)** to experiment with invariant extraction
3. **Study the [Theory Paper](https://yourusername.github.io/orthogonal-engineering/theory/)** for formal definitions

---

## 📜 Status

- ✅ **Validated** for AI chat analysis and LLM output control
- ✅ **Operational** across 251,469+ files, 233.59 GB of AI collaboration data
- ⚠️ **Theoretical extensions** remain untested
- ⚠️ **Cross-domain transfer** not yet empirically validated

---

## 🧪 Technical Details

**Built with:**
- Pure HTML/CSS/JavaScript (no frameworks)
- SQLite for chat export normalization
- Python for burst detection and timing analysis
- Pydantic for structured output validation

**Tested on:**
- ChatGPT exports (JSON)
- Claude exports (various formats)
- Custom AI conversation archives
- Real-time LLM API responses

---

## 📝 License

Work in progress · Structural document · Not peer reviewed

---

## 🤝 Contributing

This is a living methodology. If you've applied orthogonal engineering to your own systems, I'd love to hear about it.

---

**Built by someone who talked to AI systems 600+ times and needed a way to extract signal from the accumulated noise.**

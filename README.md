# ORTHOGONAL ENGINEERING

**A constraint-first methodology for extracting reliable outputs from unreliable AI systems**

[![Status](https://img.shields.io/badge/status-work%20in%20progress-yellow)](CHANGELOG.md)
[![Theory](https://img.shields.io/badge/theory-mathematically%20formalized-blue)](FORMAL_FOUNDATIONS.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🎯 Core Insight

**"Don't fight LLM verbosity—build canals so the noise turns your mill."**

Instead of trying to fix AI models or suppress their drift, orthogonal engineering designs systems that channel unpredictable behavior into structured extraction paths, preserving signal while routing noise.

---

## 📊 Validation Data

- ✅ **251,469 files** analyzed
- ✅ **233.59 GB** of AI collaboration data
- ✅ **600+ conversations** processed
- ✅ **3,842+ messages** normalized from ChatGPT/Claude exports
- ✅ Burst detection confirmed operational
- ✅ Invariant extraction validated
- ✅ Timing analysis working
- ✅ Mathematical foundations formalized

---

## 🔗 Live Demos

**Main Guide:**
- Interactive demonstration of the methodology
- Copy-paste canal templates
- Visual flow diagrams
- [View Main Guide](https://yourusername.github.io/orthogonal-engineering/)

**Theory Paper:**
- Formal structural analysis (v3)
- Benevolent Absence Theorem
- Algorithm descriptions
- [View Theory Paper](https://yourusername.github.io/orthogonal-engineering/theory/)

**Workbench Tool:**
- Minimal interactive extraction interface
- Paste prompt + output, get invariants
- No network, no storage, pure client-side
- [View Workbench](https://yourusername.github.io/orthogonal-engineering/workbench/)

---

## 🧬 Core Concepts

### Benevolent Absence
The LLM will not perfectly self-correct. Help in that form is ontologically absent. We must engineer around this reality, not fight it.

### Invariant
A structural property of system output that remains stable under constraint-induced drift and can be extracted without semantic correction.

### Canal Architecture
A structural pathway that diverts entropy, drift, or verbosity away from the analysis layer while allowing invariant signal to pass through.

---

## 🎓 Formal Mathematical Foundations

Orthogonal engineering now has a **complete mathematical framework** with formal definitions, theorems, and proofs. 

**See [FORMAL_FOUNDATIONS.md](FORMAL_FOUNDATIONS.md) for:**

- **Mathematical Definitions:**
  - Formal definition of invariants as stable output properties
  - Canal architecture as drift-routing functions
  - Drift dynamics and signal preservation

- **Proven Theorems:**
  - **Benevolent Absence Theorem**: Systems with constraint-induced drift can be made reliable through structural extraction
  - **Signal Preservation Theorem**: Properly designed canals preserve invariant content under bounded drift
  - **Drift Routing Theorem**: Canal architectures successfully route noise away from extraction layers

- **Computational Complexity:**
  - O(n) extraction time for pattern-based canals
  - O(n log n) for parsing-based extraction
  - Memory bounds and optimization strategies

- **Formal Proofs:**
  - Complete mathematical proofs of all theorems
  - Rigorous analysis of canal properties
  - Invariant stability guarantees under specified constraints

**Status:** Theoretical foundations complete ✅ | Peer review pending ⚠️

---

## 🔄 The Methodology

### Layer 0: Input Canal (Pre-Generation)
Shape the input before generation starts—force the model to begin inside the ditch instead of being coaxed into it afterward.

```
###USER_QUERY###
{{user_input}}
###END_QUERY###
```

### Layer 1: Raw LLM Output
```
[INVARIANT] The core answer you need...[/INVARIANT]

...but surrounded by drift, padding, attribution, over-explanation, 
unnecessary context, hedging, and verbose elaboration...
```

### Layer 2: Post-Processing & Extraction
```python
import re

def extract_invariant(llm_output):
    pattern = r'\[INVARIANT\](.*?)\[/INVARIANT\]'
    match = re.search(pattern, llm_output, re.DOTALL)
    return match.group(1).strip() if match else None
```

### Layer 3: Raised Fields (Templates & Structure)
```
Answer: [X]
Context: [Y]

Drift flows into [Y], leaving [X] clean.
```

### Layer 4: Iterative Refinement
Use the extracted invariant as seed for a new, more constrained query. Each cycle raises the field higher—further from drift.

---

## 🛠️ Canal Kits: Ready-Made Templates

### Enum Extraction
```python
from enum import Enum
from pydantic import BaseModel

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class SentimentOutput(BaseModel):
    sentiment: Sentiment
    confidence: float
```

### Date Extraction
```python
from datetime import date
from pydantic import BaseModel

class DateOutput(BaseModel):
    event_date: date
    timezone: str
    all_day: bool
```

### SQL Query Extraction
```python
from pydantic import BaseModel, validator

class SQLOutput(BaseModel):
    query: str
    parameters: dict
    explanation: str
    
    @validator('query')
    def validate_sql(cls, v):
        forbidden = ['DROP', 'DELETE', 'TRUNCATE']
        if any(word in v.upper() for word in forbidden):
            raise ValueError('Unsafe SQL operation')
        return v
```

---

## 📁 Repository Structure

```
orthogonal-engineering/
│
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── CHANGELOG.md               # Version history and roadmap
├── DEPLOYMENT_GUIDE.md        # Step-by-step GitHub setup
├── QUICK_REFERENCE.md         # Sharing templates and quick links
├── INVARIANTS.md              # Invariant classification methodology
├── FAILURES.md                # Known failure modes and limitations
├── REPRODUCE.md               # How to reproduce validation
├── FORMAL_FOUNDATIONS.md      # Mathematical framework and proofs
├── DATA_FILESYSTEM.md         # 🆕 Empirical grounding (251K+ files analyzed)
├── AGENT_IN_IDE.md            # 🆕 IDE agent integration profile
│
├── index.html                 # MAIN GUIDE - Full methodology
│
├── theory/
│   └── index.html            # THEORY PAPER (v3) - Formal analysis
│
├── workbench/
│   └── index.html            # WORKBENCH TOOL (v4) - Extraction interface
│
├── ontology/
│   └── orthogonal_ontology.json  # 🆕 Formal schema for IDE agents
│
├── analysis/
│   ├── README.md             # 🆕 Analysis scripts documentation
│   ├── analyze_filesystem_invariants.py  # 🆕 Canal structure detection
│   └── analyze_conversation_patterns.py   # 🆕 Turn-taking & depth analysis
│
└── data/
    ├── DATA_SCHEMA.md        # 🆕 Data schema documentation
    ├── filesystem_invariants_analysis.json  # 🆕 Generated analysis
    └── conversation_patterns_analysis.json   # 🆕 Generated analysis
```

---

## 🧪 Validated Implementations

1. **SQLite Canal for Chat Export Normalization**
   - Processes ChatGPT and Claude conversation exports
   - Handles multiple export formats
   - Normalizes timestamps and message structure

2. **DSCA Timing Analysis**
   - Burst detection (temporal clustering)
   - Turn-taking pattern recognition
   - Session boundary identification

3. **LLM API Output Controller**
   - Structured output enforcement
   - Violation logging
   - Constraint validation

---

## ⚠️ Known Limitations

- Cross-domain transfer not yet empirically validated beyond AI conversations
- Invariant detection currently requires human judgment
- Evaluation limited to personal LLM datasets (251K+ files)
- Theoretical framework complete but not yet peer-reviewed
- No standard library or plug-and-play framework
- Requires technical expertise to implement

See [FAILURES.md](FAILURES.md) for complete catalog of failure modes.

---

## 🚀 Getting Started

### 1. Explore the Demos
- [Main Guide](https://yourusername.github.io/orthogonal-engineering/) - Interactive walkthrough
- [Workbench](https://yourusername.github.io/orthogonal-engineering/workbench/) - Try extraction yourself

### 2. Read the Theory
- [Theory Paper](https://yourusername.github.io/orthogonal-engineering/theory/) - Formal analysis
- [FORMAL_FOUNDATIONS.md](FORMAL_FOUNDATIONS.md) - Mathematical framework
- [INVARIANTS.md](INVARIANTS.md) - Classification methodology

### 3. Apply to Your Work
- Start with simple templates
- Test extraction on your LLM outputs
- Iterate on canal designs
- Document what works (and what doesn't)

### 4. Reproduce the Validation
- See [REPRODUCE.md](REPRODUCE.md) for detailed instructions
- Apply methodology to your own datasets
- Share your findings

---

## 📚 Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Version history and roadmap
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - How to deploy your own instance
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - One-page overview and sharing templates
- **[INVARIANTS.md](INVARIANTS.md)** - What qualifies as INVARIANT vs CRAFTSMAN
- **[FAILURES.md](FAILURES.md)** - Where the methodology fails
- **[REPRODUCE.md](REPRODUCE.md)** - How to validate the approach yourself
- **[FORMAL_FOUNDATIONS.md](FORMAL_FOUNDATIONS.md)** - Complete mathematical framework
- **[DATA_FILESYSTEM.md](DATA_FILESYSTEM.md)** 🆕 - Empirical grounding (251K+ files, 538 conversations)
- **[AGENT_IN_IDE.md](AGENT_IN_IDE.md)** 🆕 - IDE agent integration (causal traces, invariants, state machine)

---

## 🤝 Contributing

This is a living methodology. Contributions welcome:

- Share your canal templates
- Report failure modes
- Suggest refinements to theory
- Test in new domains
- Improve documentation

Open an issue or pull request to get involved.

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🏆 Status

- **v0.2.0** - Theoretical foundations complete
- **Work in progress** - Cross-domain validation ongoing
- **Not peer-reviewed** - Academic publication pending
- **Validated** - 600+ conversations, 233GB of real data

---

## 💬 Contact

- **GitHub Issues**: For questions, bug reports, feature requests
- **Discussions**: For methodology questions and use cases
- **Pull Requests**: For contributions and improvements

---

**Built with LOGOS first principles: Deterministic, inspectable, ideology-agnostic.**

**"You are not fixing the model. You are engineering around its nature."**

---
tags: [minimal-ai-ide, logos-ide-readme]
register: documentation
---

# Logos IDE - Minimal AI IDE with Textual TUI

## Overview

Logos IDE is a terminal-based Integrated Development Environment designed for efficiency and auditability. It handles 22k+ files without performance degradation and integrates AI communication with cryptographic invariant verification.

**Principle**: "Minimum viable IDE" - not a VS Code competitor, just the essentials you need.

## Features

### 1. **File Navigator (Search-based, not Tree)**
- Indexes 22k+ files once on startup
- Fuzzy search through file names
- Shows max 50 results at a time
- Lazy loading of file content
- File icons based on extension (🐍 Python, ⚙️ C++, etc.)

### 2. **Editor Pane**
- Syntax highlighting for Python, C++, JavaScript, TypeScript, HTML, CSS, Markdown, JSON, YAML
- Auto-detects language from file extension
- Line numbers and proper indentation
- Ctrl+S to save (triggers git status update)

### 3. **AI Panel with Logos Proxy**
- Integrated Logos Proxy for bijective invariant auditing
- Every AI exchange creates verifiable cryptographic hash
- Links prompt, response, timestamp, and git state
- Shows last 10 audit entries from `corporate_audits/logos_audit.jsonl`
- "Verify Invariant" button to check integrity

### 4. **Status Bar**
- Left: Current git commit (short hash)
- Center: Current file path
- Right: Last invariant hash (first 8 chars)
- Updates automatically on file changes and AI interactions

## Performance Design

Given 22k files:
- **Never** uses `os.walk` on every keystroke
- Indexes files once on startup
- Filters with list comprehension: `[f for f in self.file_index if query in f.name]`
- Lazy loads file content (doesn't read 3k files into RAM)
- Search limited to 50 results for instant response

## Installation

### Prerequisites
- Python 3.8+
- Git (for commit tracking)

### Setup
```bash
# Clone the repository
cd minimal_ai_ide

# Install requirements
pip install -r requirements_v57.txt

# Set DeepSeek API key (optional, for AI features)
set DEEPSEEK_API_KEY=your_key_here  # Windows
# or
export DEEPSEEK_API_KEY=your_key_here  # Linux/Mac
```

## Usage

### Quick Start
```bash
# Run the launcher (Windows)
run_logos_ide.bat

# Or run directly
python logos_ide.py
```

### Key Bindings
- **Ctrl+Q**: Quit the IDE
- **Ctrl+S**: Save current file
- **Ctrl+F**: Focus file search input
- **Ctrl+A**: Focus AI input
- **F1**: Show help

### Navigation
1. **File Search**: Type in the search box to find files
2. **Open File**: Click on a file in search results to open in editor
3. **AI Chat**: Type in AI input box and press Send or Enter
4. **Verify**: Click "Verify" button to check invariant integrity

### Test Suite
```bash
# Run comprehensive tests
python test_logos_ide.py
```

## Architecture

### Core Components

```python
# File structure
logos_ide.py              # Main application
├── FileIndex            # Efficient file indexing (22k+ files)
├── FileSearcher         # Search widget with fuzzy matching
├── EditorPane          # Syntax-highlighting editor
├── AIPanel             # Logos Proxy integration
└── StatusBar           # Git commit + invariant display

logos_proxy.py           # Bijective invariant auditing
direct_deepseek_chat.py  # DeepSeek API client
```

### Audit System
Every AI interaction creates an immutable audit trail:
```json
{
  "timestamp": "2024-02-01T12:00:00Z",
  "git_commit": "a1b2c3d4",
  "prompt_hash": "sha256...",
  "response_hash": "sha256...",
  "composite_invariant": "sha256(prompt||response||timestamp||git_commit)",
  "api_success": true,
  "model": "deepseek-chat",
  "constraint_enabled": true
}
```

## Integration Points

### 1. **Git Integration**
- Automatically detects git repository
- Shows current commit hash in status bar
- Updates on file save

### 2. **Audit Trail Integration**
- Reads from `corporate_audits/logos_audit.jsonl`
- Shows last 10 exchanges in AI panel
- Links each exchange to git state

### 3. **File Type Support**
- **Python**: `.py` (🐍 icon, Python syntax)
- **C/C++**: `.cpp`, `.h`, `.hpp` (⚙️ icon, C++ syntax)
- **Web**: `.js`, `.ts`, `.html`, `.css` (📜🌐🎨 icons)
- **Data**: `.json`, `.yaml`, `.yml` (📊⚙️ icons)
- **Docs**: `.md`, `.txt` (📝📄 icons)

## Performance Benchmarks

| Operation | Time (22k files) | Memory |
|-----------|------------------|--------|
| Initial index | ~5-10 seconds | ~5MB |
| File search | < 100ms | Minimal |
| File load | < 50ms | Lazy |
| AI query | API-dependent | Minimal |
| Status update | < 10ms | Minimal |

## Use Cases

### 1. **Code Review with AI**
- Open a file in editor
- Ask AI "explain this function"
- Get audited response with invariant
- Verify no tampering occurred

### 2. **Large Codebase Navigation**
- Search across 22k files instantly
- Open and edit files
- See git context for each file

### 3. **Audited AI Development**
- Every AI suggestion is cryptographically logged
- Can prove "I asked about this function at invariant X"
- Tamper-evident audit trail

## Troubleshooting

### Common Issues

1. **"LogosProxy not found"**
   - Ensure `logos_proxy.py` is in the same directory
   - Check Python path includes current directory

2. **"No git repository"**
   - Status bar shows "NO_GIT"
   - Run `git init` if needed

3. **"AI features disabled"**
   - Set `DEEPSEEK_API_KEY` environment variable
   - Or use without AI (file search and editor still work)

4. **Performance issues with 22k+ files**
   - Initial index takes time (once per session)
   - Subsequent searches are fast
   - Reduce search limit in `FileIndex.search()`

### Testing
```bash
# Run full test suite
python test_logos_ide.py

# Test individual components
python -c "from logos_ide import FileIndex; print('FileIndex OK')"
python -c "from logos_proxy import LogosProxy; print('LogosProxy OK')"
```

## Design Philosophy

### 1. **Minimalism**
- No web frameworks (Flask/Django)
- No Electron (terminal-native)
- No database (JSONL is database)
- No LSP servers (keep it simple)

### 2. **Auditability**
- Every AI exchange creates verifiable invariant
- Links to git state for reproducibility
- Immutable audit trail
- Tamper-evident design

### 3. **Performance**
- Index once, search many
- Lazy loading
- Memory-efficient data structures
- Terminal-native (no browser overhead)

## Future Enhancements

### Planned Features
1. **Multi-file search**: Search within file contents
2. **Project switching**: Switch between different codebases
3. **Custom themes**: Additional Textual themes
4. **Plugin system**: Extend with Python modules
5. **Batch operations**: Apply AI suggestions across files

### Extensibility
The modular design allows easy extension:
- Add new file types to `FileIndex.file_extensions`
- Add syntax highlighting for new languages
- Integrate additional AI providers
- Custom audit backends

## License & Credits

**Logos IDE** is part of the Orthogonal Engineering project.

**Key Technologies**:
- [Textual](https://textual.textualize.io/) - Terminal UI framework
- [DeepSeek API](https://platform.deepseek.com/) - AI provider
- Standard Python libraries

**Architecture**: Based on "Minimum Viable IDE" concept by Kimi AI.

---

**🚀 Ready to use?** Run `python logos_ide.py` or `run_logos_ide.bat` to start!
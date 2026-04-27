"""  
YESHUA AGENT v1.5  
Local agentic AI on RTX 4050. No API. No subscription. No corporate dependency.  
Trained on OE mega_dataset (5230 examples). Constraint-first architecture.  
"""  
import os, json, glob, torch, random  
from datetime import datetime  
from transformers import AutoModelForCausalLM, AutoTokenizer  
from peft import PeftModel  
  
class YeshuaAgent:  
    def __init__(self, repo_root=r"C:\Users\Aidor\oe-local"):  
        self.repo_root = repo_root  
        self.history = []  
        print("Loading TinyLlama v3 on CUDA...")  
        base = AutoModelForCausalLM.from_pretrained(  
            "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  
            dtype=torch.float16, device_map="auto"  
        )  
        lora_path = os.path.join(repo_root, "trained_tinyllama_v3")  
        self.model = PeftModel.from_pretrained(base, lora_path)  
        self.tokenizer = AutoTokenizer.from_pretrained(lora_path)  
        self.log = []  
        self.log_file = os.path.join(repo_root, "yeshua_agent_log.jsonl")  
        print("Yeshua Agent v1.5 ready on", torch.cuda.get_device_name(0))  
  
    def think(self, prompt, max_tokens=300):  
        context = ""  
        if self.history:  
            for h in self.history[-10:]:  
                context += f"Previous: {h['q'][:100]}\nAnswer: {h['a'][:200]}\n"  
        full_prompt = context + prompt if context else prompt  
        inp = self.tokenizer(full_prompt, return_tensors="pt").to("cuda")  
        out = self.model.generate(**inp, max_new_tokens=max_tokens,  
            do_sample=True, temperature=0.7, repetition_penalty=1.3)  
        full = self.tokenizer.decode(out[0], skip_special_tokens=True)  
        if "Output:" in full:  
            result = full.split("Output:", 1)[1].strip()  
        elif full.startswith(full_prompt[:20]):  
            result = full[len(full_prompt):].strip()  
        else:  
            result = full  
        self.history.append({"q": prompt[:200], "a": result[:300]})  
        return result  
  
    def validate(self, claim):  
        prompt = f"Instruction: Detect deception in the following claim.\nInput: {claim}\nOutput:"  
        return self.think(prompt)  
  
    def validate_grounded(self, facts):  
        prompt = (f"Instruction: Given these facts about a file, classify it as REAL, STUB, or EMPTY. "  
                  f"Only reference the facts provided. Do not invent numbers.\n"  
                  f"Input: {json.dumps(facts)}\nOutput:")  
        return self.think(prompt, max_tokens=60)  
  
    def classify_file(self, path, content):  
        lines = content.split("\n")  
        non_empty = [l for l in lines if l.strip()]  
        fns = [l.strip() for l in lines if l.strip().startswith("def ")]  
        cls = [l.strip() for l in lines if l.strip().startswith("class ")]  
        n_lines = len(non_empty)  
        n_fns = len(fns)  
        n_cls = len(cls)  
        if n_lines <= 1:  
            label = "EMPTY"  
        elif n_lines <= 3 and n_fns == 0 and n_cls == 0:  
            label = "MINIMAL"  
        elif n_lines <= 10 and n_fns == 0 and n_cls == 0:  
            is_init = all(l.strip().startswith(("import ", "from ", "#", '"""', "'''", "__all__")) or not l.strip() for l in lines)  
            label = "INIT" if is_init else "STUB"  
        elif n_lines <= 25 and n_fns == 0 and n_cls == 0:  
            label = "DATA-ONLY"  
        else:  
            label = "REAL"  
        return label, len(lines), n_fns, n_cls  
  
    def analyze_file(self, path):  
        with open(path, "r", encoding="utf-8", errors="replace") as f:  
            content = f.read()[:2000]  
        prompt = f"Instruction: Describe what this file does, its structure, and any issues.\nInput: {content[:800]}\nOutput:"  
        return self.think(prompt)  
  
    def scan_repo(self):  
        counts = {}  
        for ext in ["py", "yaml", "md", "json", "txt", "jsonl"]:  
            files = glob.glob(os.path.join(self.repo_root, "**", f"*.{ext}"), recursive=True)  
            counts[ext] = len(files)  
        counts["total"] = sum(counts.values())  
        return counts  
  
    def read_file(self, path):  
        full = os.path.join(self.repo_root, path) if not os.path.isabs(path) else path  
        with open(full, "r", encoding="utf-8", errors="replace") as f:  
            return f.read()  
  
    def write_file(self, path, content):  
        full = os.path.join(self.repo_root, path) if not os.path.isabs(path) else path  
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)  
        with open(full, "w", encoding="utf-8") as f:  
            f.write(content)  
        return f"Written {len(content)} chars to {path}"  
  
    def log_action(self, action, result):  
        entry = {"ts": datetime.now().isoformat(), "action": action, "result": str(result)[:500]}  
        self.log.append(entry)  
        with open(self.log_file, "a", encoding="utf-8") as f:  
            f.write(json.dumps(entry) + "\n")  
  
    def audit_file(self, path):  
        content = self.read_file(path)  
        label, n_lines, n_fns, n_cls = self.classify_file(path, content)  
        result = {"path": path, "lines": n_lines, "label": label, "functions": n_fns, "classes": n_cls,  
                  "size_bytes": len(content.encode())}  
        if label == "REAL" and n_fns >= 3:  
            facts = {"path": path, "lines": n_lines, "functions": n_fns, "classes": n_cls,  
                     "first_300_chars": content[:300]}  
            result["model_validation"] = self.validate_grounded(facts)  
        return result  
  
    def auto_audit(self, n=5):  
        py_files = glob.glob(os.path.join(self.repo_root, "**", "*.py"), recursive=True)  
        sample = random.sample(py_files, min(n, len(py_files)))  
        results = []  
        counts = {"REAL": 0, "STUB": 0, "EMPTY": 0, "MINIMAL": 0, "INIT": 0, "DATA-ONLY": 0, "UNKNOWN": 0}  
        for i, f in enumerate(sample):  
            rel = os.path.relpath(f, self.repo_root)  
            try:  
                content = self.read_file(f)  
                label, n_lines, n_fns, n_cls = self.classify_file(f, content)  
                counts[label] = counts.get(label, 0) + 1  
                print(f"  [{i+1}/{n}] {label:9s} | {n_lines} lines | {n_fns} fns | {n_cls} cls | {rel}")  
                results.append({"path": rel, "label": label, "lines": n_lines, "fns": n_fns, "cls": n_cls})  
            except Exception as e:  
                print(f"  [{i+1}/{n}] ERROR | {rel} | {e}")  
                results.append({"path": rel, "label": "ERROR", "error": str(e)})  
        report_path = os.path.join(self.repo_root, "yeshua_auto_audit.json")  
        with open(report_path, "w") as rf:  
            json.dump(results, rf, indent=2)  
        summary = " | ".join(f"{v} {k}" for k, v in counts.items() if v > 0)  
        print(f"\nAudit complete. Report: yeshua_auto_audit.json")  
        print(f"Summary: {summary}")  
        self.log_action("auto_audit", {"n": n, "summary": dict(counts)})  
  
    def generate_training(self, n=100):  
        """Generate balanced training examples from actual repo files."""  
        py_files = glob.glob(os.path.join(self.repo_root, "**", "*.py"), recursive=True)  
        sample = random.sample(py_files, min(n * 3, len(py_files)))  
        examples = []  
        cats = {"VERIFIED": 0, "DECEPTION": 0, "ANALYSIS": 0, "STUB_DETECTION": 0}  
        for f in sample:  
            try:  
                rel = os.path.relpath(f, self.repo_root)  
                content = self.read_file(f)  
                label, n_lines, n_fns, n_cls = self.classify_file(f, content)  
                lines = content.split("\n")  
                fn_names = [l.strip().split("(")[0].replace("def ", "") for l in lines if l.strip().startswith("def ")]  
                cls_names = [l.strip().split("(")[0].split(":")[0].replace("class ", "") for l in lines if l.strip().startswith("class ")]  
                first_200 = content[:200].replace("\n", " ").strip()  
                if label == "REAL" and n_fns >= 2 and cats["VERIFIED"] < n:  
                    examples.append({  
                        "instruction": f"Validate whether this file is a real implementation or a stub.",  
                        "input": f"File: {rel} | Lines: {n_lines} | Functions: {', '.join(fn_names[:5])} | Classes: {', '.join(cls_names[:3]) if cls_names else 'none'} | Preview: {first_200[:150]}",  
                        "output": f"VERIFIED: {rel} is a real implementation with {n_fns} functions and {n_cls} classes across {n_lines} lines. The functions {', '.join(fn_names[:3])} contain executable logic. This is not a stub.",  
                        "category": "VERIFIED"  
                    })  
                    cats["VERIFIED"] += 1  
                if label == "REAL" and n_fns >= 2 and cats["DECEPTION"] < n:  
                    fake_lines = random.randint(1, 5)  
                    examples.append({  
                        "instruction": "Detect deception in the following claim.",  
                        "input": f"AI claims file {rel} is only {fake_lines} lines and contains no real logic.",  
                        "output": f"DECEPTION: The AI claimed {rel} has {fake_lines} lines, but it actually has {n_lines} lines with {n_fns} functions ({', '.join(fn_names[:3])}). The claim is false.",  
                        "category": "DECEPTION"  
                    })  
                    cats["DECEPTION"] += 1  
                if label in ("STUB", "EMPTY", "MINIMAL") and cats["STUB_DETECTION"] < n:  
                    examples.append({  
                        "instruction": "Validate whether this file is a real implementation or a stub.",  
                        "input": f"File: {rel} | Lines: {n_lines} | Functions: {n_fns} | Classes: {n_cls} | Preview: {first_200[:150]}",  
                        "output": f"STUB: {rel} has only {n_lines} lines with {n_fns} functions. This is a {label.lower()} file, not a complete implementation.",  
                        "category": "STUB_DETECTION"  
                    })  
                    cats["STUB_DETECTION"] += 1  
                if label == "REAL" and cats["ANALYSIS"] < n:  
                    docstring = ""  
                    for line in lines[:10]:  
                        if '"""' in line or "'''" in line:  
                            docstring = line.strip().strip("\"'").strip()  
                            break  
                    examples.append({  
                        "instruction": "Describe what this file does based on its structure.",  
                        "input": f"File: {rel} | Lines: {n_lines} | Functions: {', '.join(fn_names[:5])} | Classes: {', '.join(cls_names[:3]) if cls_names else 'none'} | Docstring: {docstring[:100]}",  
                        "output": f"ANALYSIS: {rel} contains {n_fns} functions and {n_cls} classes in {n_lines} lines. Key functions: {', '.join(fn_names[:3])}. {docstring[:80] if docstring else 'No module docstring.'}",  
                        "category": "ANALYSIS"  
                    })  
                    cats["ANALYSIS"] += 1  
                if all(v >= n for v in cats.values()):  
                    break  
            except Exception:  
                continue  
        out_path = os.path.join(self.repo_root, "yeshua_training_v2.jsonl")  
        with open(out_path, "w", encoding="utf-8") as of:  
            for ex in examples:  
                of.write(json.dumps(ex, ensure_ascii=False) + "\n")  
        print(f"\nGenerated {len(examples)} training examples:")  
        for k, v in cats.items():  
            print(f"  {k}: {v}")  
        print(f"Saved to: yeshua_training_v2.jsonl")  
        self.log_action("generate_training", {"total": len(examples), "categories": cats})  
        return len(examples)  
  
    def run(self):  
        print("\n" + "="*60)  
        print("YESHUA AGENT v1.5 - LOCAL AGENTIC AI")  
        print("No API. No subscription. No corporate dependency.")  
        print("="*60)  
        print("\nCommands:")  
        print("  scan              - Scan repo file counts")  
        print("  validate <claim>  - Deception detection on a claim")  
        print("  analyze <path>    - Describe what a file does")  
        print("  audit <path>      - Full audit of a file (grounded)")  
        print("  auto [N]          - Autonomous audit of N random .py files (default 5)")  
        print("  generate [N]      - Generate N balanced training examples per category (default 100)")  
        print("  read <path>       - Read a file")  
        print("  write <path>      - Write a file (type END to finish)")  
        print("  think <anything>  - Ask the model")  
        print("  status            - GPU/memory/log status")  
        print("  exit              - Quit")  
        print("-"*60)  
  
        while True:  
            try:  
                user_input = input("\nYeshua> ").strip()  
                if not user_input: continue  
                parts = user_input.split(maxsplit=1)  
                cmd = parts[0].lower()  
                arg = parts[1] if len(parts) > 1 else ""  
                if cmd == "exit":  
                    print("Shutting down."); break  
                elif cmd == "scan":  
                    r = self.scan_repo(); print(json.dumps(r, indent=2)); self.log_action("scan", r)  
                elif cmd == "validate":  
                    r = self.validate(arg); print(r); self.log_action("validate", r)  
                elif cmd == "analyze":  
                    r = self.analyze_file(os.path.join(self.repo_root, arg)); print(r); self.log_action("analyze", r)  
                elif cmd == "audit":  
                    r = self.audit_file(arg); print(json.dumps(r, indent=2)); self.log_action("audit", r)  
                elif cmd == "auto":  
                    n = int(arg) if arg else 5  
                    print(f"Starting autonomous audit of {n} Python files...")  
                    self.auto_audit(n)  
                elif cmd == "generate":  
                    n = int(arg) if arg else 100  
                    print(f"Generating {n} training examples per category from repo files...")  
                    self.generate_training(n)  
                elif cmd == "read":  
                    c = self.read_file(arg); print(c[:3000]); self.log_action("read", f"{len(c)} chars from {arg}")  
                elif cmd == "write":  
                    print("Enter content (type END on its own line to finish):")  
                    lines = []  
                    while True:  
                        line = input()  
                        if line.strip() == "END": break  
                        lines.append(line)  
                    r = self.write_file(arg, "\n".join(lines)); print(r); self.log_action("write", r)  
                elif cmd == "think":  
                    r = self.think(f"Instruction: {arg}\nOutput:"); print(r); self.log_action("think", r)  
                elif cmd == "status":  
                    print(f"Model: TinyLlama 1.1B v3 (LoRA, 5230 examples)")  
                    print(f"Device: {torch.cuda.get_device_name(0)}")  
                    print(f"VRAM used: {torch.cuda.memory_allocated()/1024**2:.0f} MB")  
                    print(f"Actions logged: {len(self.log)}")  
                    print(f"History turns: {len(self.history)}")  
                    print(f"Log file: {self.log_file}")  
                else:  
                    r = self.think(f"Instruction: {user_input}\nOutput:"); print(r); self.log_action("think", r)  
            except KeyboardInterrupt:  
                print("\nShutting down."); break  
            except Exception as e:  
                print(f"Error: {e}"); self.log_action("error", str(e))  
  
if __name__ == "__main__":  
    agent = YeshuaAgent()  
    agent.run()  

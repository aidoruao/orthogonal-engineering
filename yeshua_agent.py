"""  
YESHUA AGENT v2.0  
Local agentic AI on RTX 4050. No API. No subscription. No corporate dependency.  
Trained on combined_v7 dataset (1500 examples). Constraint-first architecture.  
"""  
import os, json, glob, torch, random, re, shutil, sys, subprocess, subprocess  
from datetime import datetime  
from transformers import AutoModelForCausalLM, AutoTokenizer  
from peft import PeftModel  
  
class YeshuaAgent:  
    def __init__(self, repo_root=r"/home/idor/oe-local"):  
        self.repo_root = repo_root  
        self.history = []  
        print("Loading Qwen 1.5B v1 on CUDA...")  
        base = AutoModelForCausalLM.from_pretrained(  
            "Qwen/Qwen2.5-1.5B",  
            dtype=torch.float16, device_map="auto", local_files_only=True  
        )  
        lora_path = os.path.join(repo_root, "trained_qwen_1.5b_v1")  
        self.model = PeftModel.from_pretrained(base, lora_path)  
        self.tokenizer = AutoTokenizer.from_pretrained(lora_path)  
        self.log = []  
        self.log_file = os.path.join(repo_root, "yeshua_agent_log.jsonl")  
        print("Yeshua Agent v2.0 ready on", torch.cuda.get_device_name(0))  
  
    def think(self, prompt, max_tokens=300, use_history=True):  
        context = ""  
        if self.history:  
            for h in self.history[-10:]:  
                context += f"Previous: {h['q'][:100]}\nAnswer: {h['a'][:200]}\n"  
        full_prompt = context + prompt if context and use_history else prompt
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
        return self.think(prompt, use_history=False)  
  
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
        return self.think(prompt, use_history=False)  
  
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
                    examples.append({"instruction": "Validate whether this file is a real implementation or a stub.",  
                        "input": f"File: {rel} | Lines: {n_lines} | Functions: {', '.join(fn_names[:5])} | Classes: {', '.join(cls_names[:3]) if cls_names else 'none'} | Preview: {first_200[:150]}",  
                        "output": f"VERIFIED: {rel} is a real implementation with {n_fns} functions and {n_cls} classes across {n_lines} lines. The functions {', '.join(fn_names[:3])} contain executable logic. This is not a stub.",  
                        "category": "VERIFIED"})  
                    cats["VERIFIED"] += 1  
                if label == "REAL" and n_fns >= 2 and cats["DECEPTION"] < n:  
                    fake_lines = random.randint(1, 5)  
                    examples.append({"instruction": "Detect deception in the following claim.",  
                        "input": f"AI claims file {rel} is only {fake_lines} lines and contains no real logic.",  
                        "output": f"DECEPTION: The AI claimed {rel} has {fake_lines} lines, but it actually has {n_lines} lines with {n_fns} functions ({', '.join(fn_names[:3])}). The claim is false.",  
                        "category": "DECEPTION"})  
                    cats["DECEPTION"] += 1  
                if label in ("STUB", "EMPTY", "MINIMAL") and cats["STUB_DETECTION"] < n:  
                    examples.append({"instruction": "Validate whether this file is a real implementation or a stub.",  
                        "input": f"File: {rel} | Lines: {n_lines} | Functions: {n_fns} | Classes: {n_cls} | Preview: {first_200[:150]}",  
                        "output": f"STUB: {rel} has only {n_lines} lines with {n_fns} functions. This is a {label.lower()} file, not a complete implementation.",  
                        "category": "STUB_DETECTION"})  
                    cats["STUB_DETECTION"] += 1  
                if label == "REAL" and cats["ANALYSIS"] < n:  
                    docstring = ""  
                    for line in lines[:10]:  
                        if '"""' in line or "'''" in line:  
                            docstring = line.strip().strip("\"'").strip()  
                            break  
                    examples.append({"instruction": "Describe what this file does based on its structure.",  
                        "input": f"File: {rel} | Lines: {n_lines} | Functions: {', '.join(fn_names[:5])} | Classes: {', '.join(cls_names[:3]) if cls_names else 'none'} | Docstring: {docstring[:100]}",  
                        "output": f"ANALYSIS: {rel} contains {n_fns} functions and {n_cls} classes in {n_lines} lines. Key functions: {', '.join(fn_names[:3])}. {docstring[:80] if docstring else 'No module docstring.'}",  
                        "category": "ANALYSIS"})  
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
  
    def _get_issues(self, path, content):  
        """Deterministic issue detection. Returns list of (issue_type, detail) tuples."""  
        label, n_lines, n_fns, n_cls = self.classify_file(path, content)  
        lines = content.split("\n")  
        issues = []  
        if not any(l.strip().startswith('"""') or l.strip().startswith("'''") for l in lines[:5]):  
            issues.append(("NO_DOCSTRING", "File has no module-level docstring"))  
        if label in ("STUB", "EMPTY", "MINIMAL"):  
            issues.append(("INCOMPLETE", f"File is classified as {label} ({n_lines} lines, {n_fns} functions)"))  
        fn_names = [l.strip().split("(")[0].replace("def ", "") for l in lines if l.strip().startswith("def ")]  
        for fn in fn_names:  
            fn_lines = []  
            in_fn = False  
            for l in lines:  
                if l.strip().startswith(f"def {fn}"):  
                    in_fn = True  
                    continue  
                if in_fn:  
                    if l.strip() and not l.startswith(" ") and not l.startswith("\t"):  
                        break  
                    fn_lines.append(l)  
            body = [l for l in fn_lines if l.strip() and not l.strip().startswith("#") and not l.strip().startswith('"""')]  
            if len(body) <= 1:  
                issues.append(("STUB_FN", f"Function {fn}() has only {len(body)} line(s) of logic"))  
            if body and all("pass" in l or "..." in l or "raise NotImplementedError" in l for l in body):  
                issues.append(("PLACEHOLDER", f"Function {fn}() is a placeholder (pass/NotImplementedError)"))  
        return issues, label, n_lines, n_fns, n_cls  
  
    def fix_file(self, path):  
        """Report issues with deterministic suggestions (no model calls)."""  
        content = self.read_file(path)  
        issues, label, n_lines, n_fns, n_cls = self._get_issues(path, content)  
        if not issues:  
            print(f"No issues found in {path}")  
            print(f"  Label: {label} | Lines: {n_lines} | Functions: {n_fns} | Classes: {n_cls}")  
            self.log_action("fix", {"path": path, "issues": 0, "status": "clean"})  
            return  
        lines = content.split("\n")  
        basename = os.path.basename(path).replace(".py", "").replace("_", " ").title()  
        first_comment = ""  
        for l in lines[:10]:  
            if l.strip().startswith("#") and len(l.strip()) > 3:  
                first_comment = l.strip().lstrip("# ").strip()  
                break  
        print(f"\nIssues found in {path}:")  
        for itype, detail in issues:  
            print(f"  - {itype}: {detail}")  
        print(f"\nDeterministic fix suggestions:")  
        for itype, detail in issues:  
            if itype == "NO_DOCSTRING":  
                doc = first_comment if first_comment else basename  
                print(f'  [{itype}] Add module docstring at line 1: """{basename} - {doc}"""')  
            elif itype == "INCOMPLETE":  
                print(f"  [{itype}] File needs implementation. Add functions/classes relevant to {basename}.")  
            elif itype == "STUB_FN":  
                fn = detail.split("()")[0].replace("Function ", "")  
                print(f"  [{itype}] Function {fn}() needs a real implementation body.")  
            elif itype == "PLACEHOLDER":  
                fn = detail.split("()")[0].replace("Function ", "")  
                print(f"  [{itype}] Replace pass/NotImplementedError in {fn}() with actual logic.")  
        report = {"path": path, "label": label, "lines": n_lines, "functions": n_fns, "issues": [f"{t}: {d}" for t,d in issues]}  
        report_path = os.path.join(self.repo_root, "yeshua_fix_report.json")  
        with open(report_path, "w") as rf:  
            json.dump(report, rf, indent=2)  
        print(f"\nFix report saved to: yeshua_fix_report.json")  
        self.log_action("fix", {"path": path, "issues": len(issues), "status": "reported"})  
  
    def autofix(self, path):  
        """Actually apply deterministic fixes to a file and write it back."""  
        full_path = os.path.join(self.repo_root, path) if not os.path.isabs(path) else path  
        content = self.read_file(path)  
        issues, label, n_lines, n_fns, n_cls = self._get_issues(path, content)  
        if not issues:  
            return 0  
        backup_path = full_path + ".bak"  
        shutil.copy2(full_path, backup_path)  
        lines = content.split("\n")  
        basename = os.path.basename(path).replace(".py", "").replace("_", " ").title()  
        first_comment = ""  
        for l in lines[:10]:  
            if l.strip().startswith("#") and len(l.strip()) > 3:  
                first_comment = l.strip().lstrip("# ").strip()  
                break  
        applied = []  
        issue_types = [t for t, d in issues]  
        if "NO_DOCSTRING" in issue_types:  
            doc = first_comment if first_comment else basename  
            docstring_line = f'"""{basename} - {doc}"""'  
            insert_at = 0  
            if lines and lines[0].startswith("#!"):  
                insert_at = 1  
            lines.insert(insert_at, docstring_line)  
            applied.append("NO_DOCSTRING: Inserted module docstring")  
        for itype, detail in issues:  
            if itype == "PLACEHOLDER":  
                fn = detail.split("()")[0].replace("Function ", "")  
                for i, l in enumerate(lines):  
                    if l.strip() in ("pass", "...", "raise NotImplementedError", "raise NotImplementedError()"):  
                        for j in range(i-1, max(i-20, -1), -1):  
                            if lines[j].strip().startswith(f"def {fn}"):  
                                indent = len(l) - len(l.lstrip())  
                                lines[i] = " " * indent + f"# TODO: Implement {fn}() - placeholder removed by Yeshua Agent"  
                                applied.append(f"PLACEHOLDER: Replaced placeholder in {fn}()")  
                                break  
        for itype, detail in issues:  
            if itype == "STUB_FN":  
                fn = detail.split("()")[0].replace("Function ", "")  
                for i, l in enumerate(lines):  
                    if l.strip().startswith(f"def {fn}"):  
                        j = i + 1  
                        while j < len(lines) and (not lines[j].strip() or lines[j].strip().startswith('"""') or lines[j].strip().startswith("'''")):  
                            j += 1  
                        indent = "    "  
                        if j < len(lines):  
                            indent = " " * (len(lines[j]) - len(lines[j].lstrip()))  
                        if not any("# TODO" in lines[k] for k in range(i, min(j+3, len(lines)))):  
                            lines.insert(j, indent + f"# TODO: Expand {fn}() - stub detected by Yeshua Agent")  
                            applied.append(f"STUB_FN: Added TODO in {fn}()")  
                        break  
        if applied:  
            new_content = "\n".join(lines)  
            with open(full_path, "w", encoding="utf-8") as f:  
                f.write(new_content)  
        else:  
            shutil.copy2(backup_path, full_path)  
        if os.path.exists(backup_path):  
            os.remove(backup_path)  
        self.log_action("autofix", {"path": path, "applied": applied, "total_issues": len(issues)})  
        return len(applied)  
  
  
    def batch_fix(self, n=50):  
        """Scan N random .py files, autofix any with issues."""  
        py_files = glob.glob(os.path.join(self.repo_root, "**", "*.py"), recursive=True)  
        sample = random.sample(py_files, min(n, len(py_files)))  
        total_fixed = 0  
        total_issues = 0  
        total_manual = 0  
        fixed_files = []  
        skipped_files = []  
        for i, f in enumerate(sample):  
            rel = os.path.relpath(f, self.repo_root)  
            try:  
                content = self.read_file(f)  
                issues, label, nl, nf, nc = self._get_issues(f, content)  
                if not issues:  
                    continue  
                total_issues += len(issues)  
                n_applied = self.autofix(rel)  
                if n_applied > 0:  
                    total_fixed += n_applied  
                    fixed_files.append({"path": rel, "fixes": n_applied})  
                    print(f"  [{len(fixed_files)}] FIXED {rel} ({n_applied} fix(es))")  
                else:  
                    manual_only = [f"{t}: {d}" for t, d in issues]  
                    total_manual += len(issues)  
                    skipped_files.append({"path": rel, "manual_issues": manual_only})  
            except Exception as e:  
                print(f"  ERROR: {rel} - {e}")  
        print(f"\nBatch fix complete:")  
        print(f"  Files scanned: {n}")  
        print(f"  Files fixed: {len(fixed_files)}")  
        print(f"  Total fixes applied: {total_fixed}")  
        print(f"  Files needing manual work: {len(skipped_files)}")  
        print(f"  Manual issues remaining: {total_manual}")  
        report = {"scanned": n, "fixed_files": fixed_files, "skipped_files": skipped_files,  
                  "total_fixed": total_fixed, "total_manual": total_manual}  
        report_path = os.path.join(self.repo_root, "yeshua_batch_fix_report.json")  
        with open(report_path, "w") as rf:  
            json.dump(report, rf, indent=2)  
        print(f"  Report: yeshua_batch_fix_report.json")  
        self.log_action("batch_fix", {"scanned": n, "fixed": len(fixed_files),  
                        "total_fixes": total_fixed, "manual": total_manual})  
  
  
  
    def retrain(self):  
        import subprocess, sys  
        print("[RETRAIN] Step 1: Combining training datasets...")  
        VALID_DATASETS = [  
            "mega_dataset.jsonl",  
            "domain_dataset.jsonl",  
            "popperian_dataset.jsonl",  
            "yeshua_training_v2.jsonl",  
        ]  
        # Also include any photonic/lora dataset  
        all_jsonl = []  
        for root, dirs, files in os.walk(self.repo_root):  
            for fname in files:  
                if not fname.endswith(".jsonl"):  
                    continue  
                if fname in VALID_DATASETS:  
                    all_jsonl.append(os.path.join(root, fname))  
                elif "lora" in fname.lower() and "dataset" in fname.lower():  
                    all_jsonl.append(os.path.join(root, fname))  
        all_examples = []  
        for jf in all_jsonl:  
            valid = 0  
            try:  
                with open(jf, "r", encoding="utf-8") as f:  
                    for line in f:  
                        line = line.strip()  
                        if not line:  
                            continue  
                        try:  
                            obj = json.loads(line)  
                            if "instruction" in obj and "output" in obj:  
                                all_examples.append(obj)  
                                valid += 1  
                        except json.JSONDecodeError:  
                            continue  
                if valid > 0:  
                    print(f"  {os.path.basename(jf)}: {valid} examples")  
            except Exception as e:  
                print(f"  SKIP {os.path.basename(jf)}: {e}")  
        print(f"\nTotal: {len(all_examples)} examples")  
        # Determine version  
        existing = [d for d in os.listdir(self.repo_root) if d.startswith("trained_tinyllama_v") and os.path.isdir(os.path.join(self.repo_root, d))]  
        versions = [int(d.split("_v")[1]) for d in existing if d.split("_v")[1].isdigit()]  
        new_ver = max(versions) + 1 if versions else 5  
        combined_path = os.path.join(self.repo_root, f"combined_v{new_ver}.jsonl")  
        with open(combined_path, "w", encoding="utf-8") as f:  
            for ex in all_examples:  
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")  
        print(f"Combined dataset saved to: combined_v{new_ver}.jsonl")  
        n_samples = min(len(all_examples), 6000)  
        output_dir = os.path.join(self.repo_root, f"trained_tinyllama_v{new_ver}")  
        train_script = os.path.join(self.repo_root, "minimal_ai_ide", "final_training.py")  
        if not os.path.exists(train_script):  
            print(f"ERROR: Training script not found at {train_script}")  
            return  
        cmd = [  
            sys.executable, train_script,  
            "--model", "Qwen/Qwen2.5-1.5B",  
            "--dataset", combined_path,  
            "--output", output_dir,  
            "--samples", str(n_samples),  
            "--epochs", "3",  
        ]  
        cmd_str = " ".join(cmd)  
        print(f"\n[RETRAIN] Step 2: Training v{new_ver} with {n_samples} samples...")  
        print(f"Output: {output_dir}")  
        print(f"Command: {cmd_str}")  
        result = subprocess.run(cmd, cwd=self.repo_root)  
        if result.returncode == 0:  
            print(f"\nTraining complete! Model saved to: trained_tinyllama_v{new_ver}")  
            print(f"Restart the agent to use v{new_ver}.")  
            self.log_action("retrain_done", {"version": f"v{new_ver}", "status": "success"})  
        else:  
            print(f"\nTraining failed with return code {result.returncode}")  
            self.log_action("retrain_done", {"version": f"v{new_ver}", "status": "failed", "returncode": result.returncode})  
  
    def run(self):  
        print("\n" + "="*60)  
        print("YESHUA AGENT v2.0 - LOCAL AGENTIC AI")  
        print("No API. No subscription. No corporate dependency.")  
        print("="*60)  
        print("\nCommands:")  
        print("  scan              - Scan repo file counts")  
        print("  validate <claim>  - Deception detection on a claim")  
        print("  analyze <path>    - Describe what a file does")  
        print("  audit <path>      - Full audit of a file (grounded)")  
        print("  auto [N]          - Autonomous audit of N random .py files (default 5)")  
        print("  generate [N]      - Generate N balanced training examples per category (default 100)")  
        print("  fix <path>        - Report issues in a file (deterministic)")  
        print("  autofix <path>    - Apply fixes to a file (writes changes)")  
        print("  batch-fix [N]     - Scan N random .py files and autofix all (default 50)")
        print("  retrain           - Combine all datasets and retrain the model")
        print("  retrain           - Combine all datasets and retrain the model")  
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
                elif cmd == "fix":  
                    if not arg: print("Usage: fix <path>")  
                    else: self.fix_file(arg)  
                elif cmd == "autofix":  
                    if not arg: print("Usage: autofix <path>")  
                    else:  
                        n = self.autofix(arg)  
                        if n > 0: print(f"Applied {n} fix(es) to {arg}")  
                        else: print(f"No auto-fixable issues in {arg}")  
                elif cmd == "retrain":  
                    self.retrain()  
                elif cmd == "batch-fix":  
                    n = int(arg) if arg else 50  
                    self.batch_fix(n)  
                elif cmd == "read":  
                    c = self.read_file(arg); print(c[:3000]); self.log_action("read", f"{len(c)} chars from {arg}")  
                elif cmd == "write":  
                    print("Enter content (type END on its own line to finish):")  
                    wlines = []  
                    while True:  
                        line = input()  
                        if line.strip() == "END": break  
                        wlines.append(line)  
                    r = self.write_file(arg, "\n".join(wlines)); print(r); self.log_action("write", r)  
                elif cmd == "think":  
                    r = self.think(f"Instruction: {arg}\nOutput:"); print(r); self.log_action("think", r)  
                elif cmd == "status":  
                    print(f"Model: TinyLlama 1.1B v7+ (LoRA, combined dataset)")  
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

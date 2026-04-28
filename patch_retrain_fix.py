import json, os, sys  
  
path = "yeshua_agent.py"  
with open(path, "r", encoding="utf-8") as f:  
    code = f.read()  
  
# Replace the retrain method's dataset combination logic  
old_combine = '''for jf in glob.glob(os.path.join(self.repo_root, "**", "*.jsonl"), recursive=True):  
                if os.path.basename(jf).startswith("combined_v"):  
                    continue  
                if "yeshua_agent_log" in jf:  
                    continue  
                try:  
                    with open(jf, "r", encoding="utf-8") as df:  
                        for line in df:  
                            line = line.strip()  
                            if line:  
                                ex = json.loads(line)  
                                all_examples.append(ex)  
                    print(f"  {os.path.relpath(jf, self.repo_root)}: {len(all_examples)} examples (cumulative)")  
                except Exception:  
                    pass'''  
  
new_combine = '''for jf in glob.glob(os.path.join(self.repo_root, "**", "*.jsonl"), recursive=True):  
                skip_names = ("combined_v", "yeshua_agent_log", "yeshua_batch_fix", "yeshua_fix_report", "yeshua_auto_audit")  
                if any(os.path.basename(jf).startswith(s) for s in skip_names):  
                    continue  
                try:  
                    valid = 0  
                    with open(jf, "r", encoding="utf-8") as df:  
                        for line in df:  
                            line = line.strip()  
                            if not line:  
                                continue  
                            try:  
                                ex = json.loads(line)  
                                if all(k in ex for k in ("instruction", "input", "output")):  
                                    all_examples.append(ex)  
                                    valid += 1  
                            except (json.JSONDecodeError, TypeError):  
                                continue  
                    if valid > 0:  
                        print(f"  {os.path.relpath(jf, self.repo_root)}: {valid} valid examples ({len(all_examples)} cumulative)")  
                except Exception:  
                    pass'''  
  
if old_combine in code:  
    code = code.replace(old_combine, new_combine)  
    with open(path, "w", encoding="utf-8") as f:  
        f.write(code)  
    print("Patched retrain: now validates instruction/input/output fields per line")  
else:  
    print("ERROR: Could not find the old combine block to replace")  
    print("Searching for partial match...")  
    if "cumulative" in code and "all_examples.append(ex)" in code:  
        print("Found retrain method but exact match failed - manual edit needed")  
    else:  
        print("Retrain method not found in yeshua_agent.py")  

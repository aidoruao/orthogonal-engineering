import sys, os  
  
path = r"C:\Users\Aidor\oe-local\yeshua_agent.py"  
with open(path, "r", encoding="utf-8") as f:  
    code = f.read()  
  
# 1. Add subprocess and sys imports  
code = code.replace(  
    "import os, json, glob, torch, random, re, shutil",  
    "import os, json, glob, torch, random, re, shutil, sys, subprocess"  
)  
  
# 2. Version bump  
code = code.replace("YESHUA AGENT v1.9", "YESHUA AGENT v2.0")  
code = code.replace("Yeshua Agent v1.9", "Yeshua Agent v2.0")  
code = code.replace("YESHUA AGENT v1.9 - LOCAL", "YESHUA AGENT v2.0 - LOCAL")  
  
# 3. Add retrain to help text  
code = code.replace(  
    '    print("  batch-fix [N]     - Scan N random .py files and autofix all (default 50)")',  
    '    print("  batch-fix [N]     - Scan N random .py files and autofix all (default 50)")\n        print("  retrain           - Combine all datasets and retrain the model")'  
)  
  
# 4. Add retrain command handler  
code = code.replace(  
    'elif cmd == "read":',  
    'elif cmd == "retrain":\n                    self.retrain()\n                elif cmd == "read":'  
)  
  
# 5. Add retrain method before run()  
retrain_method = '''  
    def retrain(self):  
        """Combine all .jsonl datasets and retrain the model."""  
        print("\\n[RETRAIN] Step 1: Combining datasets...")  
        all_examples = []  
        skip_prefixes = ("combined_v", "yeshua_agent_log")  
        for jf in glob.glob(os.path.join(self.repo_root, "**", "*.jsonl"), recursive=True):  
            basename = os.path.basename(jf)  
            if any(basename.startswith(p) for p in skip_prefixes):  
                continue  
            try:  
                with open(jf, "r", encoding="utf-8", errors="replace") as f:  
                    for line in f:  
                        line = line.strip()  
                        if line:  
                            try:  
                                all_examples.append(json.loads(line))  
                            except json.JSONDecodeError:  
                                pass  
                print(f"  {os.path.relpath(jf, self.repo_root)}: {len(all_examples)} examples (cumulative)")  
            except Exception as e:  
                print(f"  ERROR reading {jf}: {e}")  
        print(f"\\nTotal: {len(all_examples)} examples")  
        # Find next version number  
        existing = glob.glob(os.path.join(self.repo_root, "trained_tinyllama_v*"))  
        versions = []  
        for d in existing:  
            try:  
                v = int(os.path.basename(d).replace("trained_tinyllama_v", ""))  
                versions.append(v)  
            except ValueError:  
                pass  
        new_ver = max(versions) + 1 if versions else 5  
        combined_path = os.path.join(self.repo_root, f"combined_v{new_ver}.jsonl")  
        with open(combined_path, "w", encoding="utf-8") as f:  
            for ex in all_examples:  
                f.write(json.dumps(ex, ensure_ascii=False) + "\\n")  
        print(f"Combined dataset saved to: combined_v{new_ver}.jsonl")  
        n_samples = min(len(all_examples), 6000)  
        output_dir = os.path.join(self.repo_root, f"trained_tinyllama_v{new_ver}")  
        train_script = os.path.join(self.repo_root, "minimal_ai_ide", "final_training.py")  
        if not os.path.exists(train_script):  
            print(f"ERROR: Training script not found at {train_script}")  
            return  
        print(f"\\n[RETRAIN] Step 2: Training v{new_ver} with {n_samples} samples...")  
        print(f"Output: {output_dir}")  
        cmd = [  
            sys.executable, train_script,  
            "--model", "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  
            "--dataset", combined_path,  
            "--output", output_dir,  
            "--samples", str(n_samples),  
            "--epochs", "3"  
        ]  
        cmd_str = " ".join(cmd)  
        print(f"Command: {cmd_str}")  
        result = subprocess.run(cmd)  
        if result.returncode == 0:  
            print(f"\\nTraining complete! Model saved to: trained_tinyllama_v{new_ver}")  
            print(f"Restart the agent to use v{new_ver}.")  
            self.log_action("retrain_done", {"version": f"v{new_ver}", "status": "success"})  
        else:  
            print(f"\\nTraining failed with return code {result.returncode}")  
            self.log_action("retrain_done", {"version": f"v{new_ver}", "status": "failed", "returncode": result.returncode})  
  
'''  
  
code = code.replace(  
    "    def run(self):",  
    retrain_method + "    def run(self):"  
)  
  
# 6. Update status command  
code = code.replace(  
    'print(f"Model: TinyLlama 1.1B v4 (LoRA, 6000 examples)")',  
    'print(f"Model: TinyLlama 1.1B v4 (LoRA, 6000 examples) | retrain to upgrade")'  
)  
  
with open(path, "w", encoding="utf-8") as f:  
    f.write(code)  
  
print(f"Patched yeshua_agent.py to v2.0")  
print(f"Python executable: {sys.executable}")  
print("Added: retrain command")  

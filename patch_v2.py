import re  
  
path = r"C:\Users\Aidor\oe-local\yeshua_agent.py"  
with open(path, "r", encoding="utf-8") as f:  
    code = f.read()  
  
# 1. Version strings  
code = code.replace("YESHUA AGENT v1.9", "YESHUA AGENT v2.0")  
code = code.replace("Yeshua Agent v1.9", "Yeshua Agent v2.0")  
code = code.replace('YESHUA AGENT v1.9 - LOCAL AGENTIC AI', 'YESHUA AGENT v2.0 - LOCAL AGENTIC AI')  
  
# 2. Add local_files_only to model loading  
code = code.replace(  
    'dtype=torch.float16, device_map="auto"',  
    'torch_dtype=torch.float16, device_map="auto", local_files_only=True'  
)  
  
# 3. Add subprocess import  
if "import subprocess" not in code:  
    code = code.replace("import os, json, glob, torch, random, re, shutil",  
                        "import os, json, glob, torch, random, re, shutil, subprocess")  
  
# 4. Insert retrain method before batch_fix  
retrain_method = '''  
    def retrain(self):  
        """Combine all datasets and retrain the model."""  
        print("\\n[RETRAIN] Step 1: Finding all .jsonl datasets...")  
        jsonl_files = glob.glob(os.path.join(self.repo_root, "*.jsonl"))  
        jsonl_files += glob.glob(os.path.join(self.repo_root, "minimal_ai_ide", "*.jsonl"))  
        jsonl_files += glob.glob(os.path.join(self.repo_root, "src", "hardware", "photonic", "lora", "*.jsonl"))  
        jsonl_files = [f for f in jsonl_files if "log" not in os.path.basename(f).lower()]  
        if not jsonl_files:  
            print("ERROR: No .jsonl dataset files found.")  
            return  
        all_examples = []  
        for jf in jsonl_files:  
            count = 0  
            try:  
                with open(jf, "r", encoding="utf-8", errors="replace") as f:  
                    for line in f:  
                        line = line.strip()  
                        if not line:  
                            continue  
                        try:  
                            ex = json.loads(line)  
                            if "instruction" in ex or "input" in ex:  
                                all_examples.append(ex)  
                                count += 1  
                        except json.JSONDecodeError:  
                            continue  
            except Exception as e:  
                print(f"  SKIP {os.path.basename(jf)}: {e}")  
                continue  
            print(f"  {os.path.basename(jf)}: {count} examples")  
        if not all_examples:  
            print("ERROR: No valid training examples found.")  
            return  
        print(f"\\nTotal: {len(all_examples)} examples")  
        # Determine version number  
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
            "python", train_script,  
            "--model", "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  
            "--dataset", combined_path,  
            "--output", output_dir,  
            "--samples", str(n_samples),  
            "--epochs", "3",  
        ]  
        print(f"Command: {' '.join(cmd)}")  
        self.log_action("retrain_start", {"version": f"v{new_ver}", "examples": len(all_examples), "samples": n_samples})  
        result = subprocess.run(cmd, cwd=self.repo_root)  
        if result.returncode == 0:  
            print(f"\\nTraining complete! Model saved to: trained_tinyllama_v{new_ver}")  
            print(f"To use the new model, update lora_path in __init__ to trained_tinyllama_v{new_ver}")  
            self.log_action("retrain_done", {"version": f"v{new_ver}", "status": "success"})  
        else:  
            print(f"\\nTraining failed with return code {result.returncode}")  
            self.log_action("retrain_done", {"version": f"v{new_ver}", "status": "failed", "returncode": result.returncode})  
  
'''  
  
# Insert before batch_fix  
code = code.replace(  
    "    def batch_fix(self, n=50):",  
    retrain_method + "    def batch_fix(self, n=50):"  
)  
  
# 5. Add retrain to help menu (after batch-fix line)  
code = code.replace(  
    '  batch-fix [N]     - Scan N random .py files and autofix all (default 50)")',  
    '  batch-fix [N]     - Scan N random .py files and autofix all (default 50)")\n'  
    '        print("  retrain           - Combine all datasets and retrain the model")'  
)  
  
# 6. Add retrain command handler (after batch-fix handler)  
code = code.replace(  
    '                elif cmd == "read":',  
    '                elif cmd == "retrain":\n'  
    '                    self.retrain()\n'  
    '                elif cmd == "read":'  
)  
  
# 7. Update status to show v2.0  
code = code.replace(  
    'print(f"Model: TinyLlama 1.1B v4 (LoRA, 6000 examples)")',  
    'print(f"Model: TinyLlama 1.1B v4+ (LoRA, combined dataset)")'  
)  
  
with open(path, "w", encoding="utf-8") as f:  
    f.write(code)  
  
print("Patched yeshua_agent.py: v1.9 -> v2.0")  
print("Added: retrain command, local_files_only, subprocess import")  

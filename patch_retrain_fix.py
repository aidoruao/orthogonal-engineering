"""Patch Retrain Fix - Remove any existing retrain method (between 'def retrain' and next 'def ' at same indent)"""
﻿import sys, os  
  
path = r'C:\Users\Aidor\oe-local\yeshua_agent.py'  
with open(path, 'r', encoding='utf-8') as f:  
    code = f.read()  
  
# Remove any existing retrain method (between 'def retrain' and next 'def ' at same indent)  
import re  
code = re.sub(r'    def retrain\(self\).*?(?=    def |\nif __name__)', '', code, flags=re.DOTALL)  
  
# Remove old retrain command handler from run() if present  
code = re.sub(r"                elif cmd == .retrain.*?\n(?=                elif|                else:)", '', code, flags=re.DOTALL)  
  
# The new retrain method  
retrain_method = '''  
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
        print(f"\\nTotal: {len(all_examples)} examples")  
        # Determine version  
        existing = [d for d in os.listdir(self.repo_root) if d.startswith("trained_tinyllama_v") and os.path.isdir(os.path.join(self.repo_root, d))]  
        versions = [int(d.split("_v")[1]) for d in existing if d.split("_v")[1].isdigit()]  
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
        cmd = [  
            sys.executable, train_script,  
            "--model", "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  
            "--dataset", combined_path,  
            "--output", output_dir,  
            "--samples", str(n_samples),  
            "--epochs", "3",  
        ]  
        cmd_str = " ".join(cmd)  
        print(f"\\n[RETRAIN] Step 2: Training v{new_ver} with {n_samples} samples...")  
        print(f"Output: {output_dir}")  
        print(f"Command: {cmd_str}")  
        result = subprocess.run(cmd, cwd=self.repo_root)  
        if result.returncode == 0:  
            print(f"\\nTraining complete! Model saved to: trained_tinyllama_v{new_ver}")  
            print(f"Restart the agent to use v{new_ver}.")  
            self.log_action("retrain_done", {"version": f"v{new_ver}", "status": "success"})  
        else:  
            print(f"\\nTraining failed with return code {result.returncode}")  
            self.log_action("retrain_done", {"version": f"v{new_ver}", "status": "failed", "returncode": result.returncode})  
  
'''  
  
# Insert retrain method before run()  
code = code.replace('    def run(self):', retrain_method + '    def run(self):')  
  
# Add retrain command handler if not present  
if 'cmd == "retrain"' not in code:  
    old_handler = '                elif cmd == "batch-fix":'  
    new_handler = '''                elif cmd == "retrain":  
                    self.retrain()  
                elif cmd == "batch-fix":'''  
    code = code.replace(old_handler, new_handler)  
  
# Update version strings  
code = code.replace('YESHUA AGENT v1.9', 'YESHUA AGENT v2.0')  
code = code.replace('Yeshua Agent v1.9', 'Yeshua Agent v2.0')  
  
# Add retrain to help menu if not present  
if 'retrain' not in code.split('Commands:')[1].split('exit')[0] if 'Commands:' in code else True:  
    code = code.replace(  
        '  batch-fix [N]     - Scan N random .py files and autofix all (default 50)',  
        '  batch-fix [N]     - Scan N random .py files and autofix all (default 50)\\n  retrain           - Combine datasets and retrain the model'  
    )  
  
with open(path, 'w', encoding='utf-8') as f:  
    f.write(code)  
  
print(f'Patched yeshua_agent.py to v2.0 with retrain command')  
print(f'Python executable: {sys.executable}')  
print(f'Key fix: only includes known training datasets (mega_dataset, domain_dataset, popperian, yeshua_training_v2, *lora*dataset*)')  

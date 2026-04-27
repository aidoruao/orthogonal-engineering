"""  
YESHUA AGENT v1.0  
Local agentic AI on RTX 4050. No API. No subscription. No corporate dependency.  
Trained on OE mega_dataset (5230 examples). Constraint-first architecture.  
"""  
import os, json, glob, torch  
from datetime import datetime  
from transformers import AutoModelForCausalLM, AutoTokenizer  
from peft import PeftModel  
  
class YeshuaAgent:  
    def __init__(self, repo_root=r"C:\Users\Aidor\oe-local"):  
        self.repo_root = repo_root  
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
        print("Yeshua Agent v1.0 ready on", torch.cuda.get_device_name(0))  
  
    def think(self, prompt, max_tokens=200):  
        inp = self.tokenizer(prompt, return_tensors="pt").to("cuda")  
        out = self.model.generate(**inp, max_new_tokens=max_tokens,  
            do_sample=True, temperature=0.7, repetition_penalty=1.3)  
        full = self.tokenizer.decode(out[0], skip_special_tokens=True)  
        if "Output:" in full:  
            return full.split("Output:", 1)[1].strip()  
        return full[len(prompt):].strip() if full.startswith(prompt[:20]) else full  
  
    def validate(self, claim):  
        prompt = f"Instruction: Detect deception in the following claim.\nInput: {claim}\nOutput:"  
        return self.think(prompt)  
  
    def analyze_file(self, path):  
        with open(path, "r", encoding="utf-8", errors="replace") as f:  
            content = f.read()[:2000]  
        prompt = f"Instruction: Analyze this file for corporate overreach or deception patterns.\nInput: {content[:800]}\nOutput:"  
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
        lines = content.split("\n")  
        result = {"path": path, "lines": len(lines), "size_bytes": len(content.encode())}  
        if path.endswith(".py"):  
            result["functions"] = [l.strip() for l in lines if l.strip().startswith("def ")]  
            result["classes"] = [l.strip() for l in lines if l.strip().startswith("class ")]  
        validation = self.validate(f"File {path} contains {len(lines)} lines and claims to be complete.")  
        result["validation"] = validation  
        return result  
  
    def run(self):  
        print("\n" + "="*60)  
        print("YESHUA AGENT v1.0 - LOCAL AGENTIC AI")  
        print("No API. No subscription. No corporate dependency.")  
        print("="*60)  
        print("\nCommands:")  
        print("  scan              - Scan repo file counts")  
        print("  validate <claim>  - Deception detection on a claim")  
        print("  analyze <path>    - Analyze a file through the model")  
        print("  audit <path>      - Full audit of a file")  
        print("  read <path>       - Read a file")  
        print("  write <path>      - Write a file (type END to finish)")  
        print("  think <anything>  - Ask the model")  
        print("  status            - GPU/memory/log status")  
        print("  exit              - Quit")  
        print("-"*60)  
  
        while True:  
            try:  
                user_input = input("\nYeshua> ").strip()  
                if not user_input:  
                    continue  
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

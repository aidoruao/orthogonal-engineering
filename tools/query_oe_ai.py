"""tools/query_oe_ai.py -- OE Yeshua 1B local inference."""  
  
import sys  
from transformers import AutoModelForCausalLM, AutoTokenizer  
from peft import PeftModel  
from pathlib import Path  
  
REPO_ROOT = Path(__file__).resolve().parent.parent  
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  
ADAPTER_PATH = str(REPO_ROOT / "trained_tinyllama_v3")  
  
def query(question):  
    base = AutoModelForCausalLM.from_pretrained(MODEL_NAME)  
    model = PeftModel.from_pretrained(base, ADAPTER_PATH)  
    tok = AutoTokenizer.from_pretrained(ADAPTER_PATH)  
    prompt = f"Instruction: {question}\nInput:\nOutput:"  
    inp = tok(prompt, return_tensors="pt")  
    out = model.generate(**inp, max_new_tokens=100, do_sample=True, temperature=0.7, repetition_penalty=1.3)  
    text = tok.decode(out[0], skip_special_tokens=True)  
    # Extract just the Output: part  
    if "Output:" in text:  
        answer = text.split("Output:")[-1].strip()  
    else:  
        answer = text  
    print(answer)  
  
if __name__ == "__main__":  
    if len(sys.argv) < 2:  
        print("Usage: python tools/query_oe_ai.py 'your question'")  
        sys.exit(1)  
    query(sys.argv[1])
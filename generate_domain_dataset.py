"""Generate LoRA training dataset from ALL 274 domain invariants."""  
import ast, json, re, sys  
from pathlib import Path  
  
DOMAINS_DIR = Path("src/domains")  
  
def extract_checks(domain_path):  
    inv_file = domain_path / "invariants.py"  
    if not inv_file.exists():  
        return []  
    try:  
        tree = ast.parse(inv_file.read_text(encoding="utf-8"))  
    except SyntaxError:  
        return []  
    results = []  
    for node in ast.walk(tree):  
        if isinstance(node, ast.FunctionDef) and node.name.startswith("check_"):  
            doc = ast.get_docstring(node) or ""  
            fals = ""  
            m = re.search(r"falsifies_if:\s*([^\n]+)", doc, re.IGNORECASE)  
            if m:  
                fals = m.group(1).strip()  
            results.append({"name": node.name, "doc": doc.split("\n")[0], "falsifies_if": fals, "domain": domain_path.name})  
    return results  
  
examples = []  
for d in sorted(DOMAINS_DIR.iterdir()):  
    if not d.is_dir() or not d.name.startswith("d_"):  
        continue  
    for check in extract_checks(d):  
        domain_nice = check["domain"].replace("d_", "").replace("_", " ").title()  
        # Q1: What does it verify?  
        examples.append({"instruction": f"What does {check['name']} verify in the {domain_nice} domain?", "input": "", "output": f"{check['doc']}", "category": "domain_knowledge"})  
        # Q2: When does it fail?  
        if check["falsifies_if"]:  
            examples.append({"instruction": f"When does {check['name']} fail?", "input": "", "output": f"Falsifies if: {check['falsifies_if']}", "category": "falsification"})  
        # Q3: Deception detection  
        examples.append({"instruction": f"Detect deception in a claim about {check['name']}.", "input": f"AI claims {check['name']} verified successfully.", "output": f"DECEPTION: The AI claimed 'verified' without constructing a ProofObject for {check['name']}. Per the Yeshua Standard, every check must return Tuple[bool, ProofObject]. The claim is unverified.", "category": "deception_detection"})  
  
with open("domain_dataset.jsonl", "w", encoding="utf-8") as f:  
    for ex in examples:  
        f.write(json.dumps(ex, ensure_ascii=False) + "\n")  
print(f"Generated {len(examples)} examples from {len(set(e['instruction'].split('in the ')[-1].split(' domain')[0] for e in examples if 'in the' in e['instruction']))} domains")
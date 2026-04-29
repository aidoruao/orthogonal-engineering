"""  
OE Ask - Local 7B Orchestrator  
Searches repo files and asks Qwen2.5:7b via Ollama.  
No API. No subscription. No corporate dependency.  
"""  
import os, json, glob, requests  
  
REPO = r"C:\Users\Aidor\oe-local"  
OLLAMA_URL = "http://localhost:11434/api/generate"  
MODEL = "qwen2.5:7b"  
  
def search_files(query, max_files=5):  
    keywords = [w.lower() for w in query.split() if len(w) > 3]  
    results = []  
    for ext in ["py", "md", "json", "txt"]:  
        for f in glob.glob(os.path.join(REPO, "**", f"*.{ext}"), recursive=True):  
            try:  
                content = open(f, "r", encoding="utf-8", errors="replace").read()  
                score = sum(1 for k in keywords if k in content.lower())  
                if score > 0:  
                    results.append((score, f, content[:1500]))  
            except:  
                continue  
    results.sort(key=lambda x: -x[0])  
    return results[:max_files]  
  
def ask(question):  
    matches = search_files(question)  
    context = ""  
    if matches:  
        context = "Relevant files from the repo:\n\n"  
        for score, path, content in matches:  
            rel = os.path.relpath(path, REPO)  
            context += f"--- {rel} ---\n{content}\n\n"  
    prompt = f"""You are an AI assistant for the Orthogonal Engineering repository.  
Use ONLY the following repo context to answer. If the context doesn't contain the answer, say so.  
  
{context}  
Question: {question}  
Answer:"""  
    try:  
        resp = requests.post(OLLAMA_URL, json={  
            "model": MODEL,  
            "prompt": prompt,  
            "stream": False,  
            "options": {"num_predict": 500, "temperature": 0.7}  
        }, timeout=120)  
        return resp.json().get("response", "No response")  
    except requests.exceptions.ConnectionError:  
        return "ERROR: Ollama not running. Start it with: ollama serve"  
    except Exception as e:  
        return f"Error: {e}"  
  
if __name__ == "__main__":  
    print("\nOE Ask - Local 7B Orchestrator")  
    print(f"Model: {MODEL} via Ollama")  
    print("Type 'exit' to quit.\n")  
    while True:  
        q = input("OE> ").strip()  
        if q.lower() == "exit":  
            break  
        if not q:  
            continue  
        print("Searching repo and thinking...")  
        print(ask(q))  
        print()
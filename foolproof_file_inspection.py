import os
import pandas as pd

def inspect():
    folder = os.getcwd()
    files = [f for f in sorted(os.listdir(folder)) if os.path.isfile(f)]
    
    for filename in files:
        ext = os.path.splitext(filename)[1].lower()
        size = os.path.getsize(filename)
        print(f"\n=== FILE: {filename} === (Size: {size:,} bytes)")
        
        # Text-based preview for .py, .md, .json
        if ext in [".py", ".md", ".json"]:
            print(f"---- {ext[1:].upper()} Preview (up to 15 lines) ----")
            try:
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    for i in range(15):
                        line = f.readline()
                        if not line: break
                        print(line.strip())
            except Exception as e:
                print(f"Error reading text: {e}")
                
        elif ext == ".csv":
            print("---- CSV Table Preview ----")
            try:
                df = pd.read_csv(filename, nrows=3)
                print(df.to_string(index=False))
                # Quick row count
                with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                    count = sum(1 for _ in f)
                print(f"Total Rows: {count:,}")
            except Exception as e:
                print(f"CSV Error: {e}")
        else:
            print("Non-text file or large binary; skipping preview.")

if __name__ == "__main__":
    inspect()

import re  
  
path = 'yeshua_agent.py'  
with open(path, 'r', encoding='utf-8') as f:  
    code = f.read()  
  
# Fix 1: Change --samples 6000 to --samples 1500  
code = re.sub(r'--samples\s+6000', '--samples 1500', code)  
  
# Fix 2: Change --epochs 3 to --epochs 1  
code = re.sub(r'--epochs\s+3', '--epochs 1', code)  
  
# Fix 3: Update status line if present  
code = code.replace('6000 examples', '1500 examples')  
  
with open(path, 'w', encoding='utf-8') as f:  
    f.write(code)  
  
print('Patched retrain: --samples 1500 --epochs 1 (750 steps, ~60 min)')  

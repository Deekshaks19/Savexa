import os
import hashlib

def sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
idx = os.path.join(root, 'index.html')
sav = os.path.join(root, 'Savexa.html')
print('index exists', os.path.exists(idx))
print('Savexa exists', os.path.exists(sav))
if os.path.exists(idx) and os.path.exists(sav):
    print('index sha256', sha256(idx))
    print('Savexa sha256', sha256(sav))
    with open(idx, 'r', encoding='utf-8', errors='replace') as f1, open(sav, 'r', encoding='utf-8', errors='replace') as f2:
        l1 = f1.readlines()
        l2 = f2.readlines()
    print('index lines', len(l1), 'Savexa lines', len(l2))
    for i, (a,b) in enumerate(zip(l1, l2), start=1):
        if a != b:
            print('first diff line', i)
            print('index:', a[:200].replace('\n','\\n'))
            print('Savexa:', b[:200].replace('\n','\\n'))
            break
    else:
        if len(l1) != len(l2):
            print('no diffs in shared prefix, different lengths')
        else:
            print('files identical')

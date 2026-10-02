import os
import hashlib

root = os.path.abspath(os.getcwd())
index_path = os.path.join(root, 'index.html')
sav_path = os.path.join(root, 'Savexa.html')
print('root:', root)
print('index exists:', os.path.exists(index_path))
print('Savexa exists:', os.path.exists(sav_path))
if os.path.exists(index_path) and os.path.exists(sav_path):
    print('index sha256:', hashlib.sha256(open(index_path,'rb').read()).hexdigest())
    print('Savexa sha256:', hashlib.sha256(open(sav_path,'rb').read()).hexdigest())
    with open(index_path, 'r', encoding='utf-8', errors='replace') as f1, open(sav_path, 'r', encoding='utf-8', errors='replace') as f2:
        l1 = f1.readlines()
        l2 = f2.readlines()
    print('index len', len(l1), 'sav len', len(l2))
    for i, (a, b) in enumerate(zip(l1, l2), start=1):
        if a != b:
            print('first diff line', i)
            print('index:', a[:200].replace('\n', '\\n'))
            print('Savexa:', b[:200].replace('\n', '\\n'))
            break
    else:
        if len(l1) != len(l2):
            print('no diff in shared prefix, lengths differ')
        else:
            print('files identical')
else:
    print('one or both files missing')

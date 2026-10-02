import os
import sqlite3

base_dir = os.path.dirname(os.path.dirname(__file__))
model_path = os.path.join(base_dir, 'cv', 'aidsense', 'models', 'aidSense_model.h5')
db_path = os.path.join(base_dir, 'db.sqlite3')

print('Model path:', model_path)
print('DB path:', db_path)
print('Model exists:', os.path.exists(model_path))
print('DB exists:', os.path.exists(db_path))

print('\n== Python packages ==')
for mod in ['tensorflow', 'h5py', 'numpy', 'PIL']:
    try:
        m = __import__(mod)
        print(mod, 'OK', getattr(m, '__version__', ''))
    except Exception as e:
        print(mod, 'ERR', type(e).__name__, e)

if os.path.exists(model_path):
    print('\n== Raw HDF5 inspect ==')
    with open(model_path, 'rb') as f:
        data = f.read(8192)
        print('Header:', data[:8])
        ascii = [s.decode('ascii', errors='ignore') for s in data.split(b'\x00') if b'keras' in s or b'cls' in s or b'name' in s or b'output' in s or b'layer' in s]
        print('ASCII hits:', ascii[:20])
        if b'KerasModel' in data or b'keras_version' in data:
            print('Looks like Keras model file')
        idx = data.find(b'weights')
        print('First "weights" index:', idx)

if os.path.exists(db_path):
    print('\n== Guidance DB ==')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('SELECT count(*) FROM api_firstaidguidance')
    print('Guidance row count:', cur.fetchone()[0])
    cur.execute('SELECT injury_type FROM api_firstaidguidance ORDER BY injury_type')
    rows = [r[0] for r in cur.fetchall()]
    print('Guidance injury types:')
    for t in rows:
        print('-', t)
    conn.close()
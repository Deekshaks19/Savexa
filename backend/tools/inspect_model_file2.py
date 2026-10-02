import os
import h5py

root = os.path.abspath(os.getcwd())
model_path = os.path.join(root, 'cv', 'aidsense', 'models', 'aidSense_model.h5')
print('root:', root)
print('model_path:', model_path)
print('model exists:', os.path.exists(model_path))
if os.path.exists(model_path):
    with h5py.File(model_path, 'r') as f:
        print('top keys:', list(f.keys()))
        print('attrs keys:', list(f.attrs.keys()))
        if 'model_config' in f.attrs:
            print('model_config exists')
        if 'keras_version' in f.attrs:
            print('keras_version', f.attrs['keras_version'])
        print('\n--- GROUP/DATASET tree ---')
        def walk(name, obj):
            if isinstance(obj, h5py.Dataset):
                print('DATASET', name, obj.shape, obj.dtype)
            elif isinstance(obj, h5py.Group):
                print('GROUP', name)
        f.visititems(walk)

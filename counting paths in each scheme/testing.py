import pickle

with open('RAEKE+LB (inv_cap)_scheme', 'rb') as handle:
    b = pickle.loads(handle.read())

path_count = 0
for pair in b:
    path_count += len(b[pair])
print(path_count)

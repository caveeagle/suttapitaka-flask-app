import sqlite3
import numpy as np
import faiss

db = 'sutta-pitaka.sqlite'

CHECK = 0  # For debugiing

def build_index():
    conn = sqlite3.connect(db)
    cur = conn.cursor()

    cur.execute("SELECT chunk_id, embedding FROM embeddings")
    rows = cur.fetchall()
    conn.close()

    chunk_ids = []
    vectors = []

    for chunk_id, blob in rows:
        vec = np.frombuffer(blob, dtype=np.float32)
        chunk_ids.append(chunk_id)
        vectors.append(vec)

    X = np.vstack(vectors)

    # cosine similarity
    X /= np.linalg.norm(X, axis=1, keepdims=True)

    index = faiss.IndexFlatIP(X.shape[1])
    index.add(X)

    return index, np.array(chunk_ids)

def search(index, chunk_ids, query_vec, k=10):
    q = np.array(query_vec, dtype=np.float32)
    q /= np.linalg.norm(q)

    scores, idxs = index.search(q[None, :], k)
    
    return (
        chunk_ids[idxs[0]].tolist(),   # < list[int]
        scores[0].tolist()
    )
    
if(CHECK):
    
    index, chunk_ids = build_index()
    
    print(f'Make {index.ntotal} indexes')
    
    assert index.ntotal > 10
    
    assert len(chunk_ids) == index.ntotal
    
    print(f'Job done')

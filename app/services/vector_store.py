import faiss
import numpy as np
import pickle
import os

def store_embeddings(embeddings: list[list[float]], chunks: list[str], pdf_id: str):
    """
    Stores embeddings in a FAISS index and saves the index and chunks to disk.
    """
    # Create a FAISS index
    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(np.array(embeddings))
    
    # Save the index and chunks
    faiss.write_index(index, os.path.join("data", "storage", f"{pdf_id}.index"))
    with open(os.path.join("data", "storage", f"{pdf_id}_chunks.pkl"), "wb") as f:
        pickle.dump(chunks, f)

def load_embeddings(pdf_id: str):
    """
    Loads the FAISS index and chunks for a given PDF.
    """
    index_path = os.path.join("data", "storage", f"{pdf_id}.index")
    chunks_path = os.path.join("data", "storage", f"{pdf_id}_chunks.pkl")
    
    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        return None, None
    
    index = faiss.read_index(index_path)
    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)
    
    return index, chunks

def search_similar_chunks(query_embedding: list[float], index: faiss.Index, chunks: list[str], top_k: int = 3):
    """
    Searches for the top_k most similar chunks to the query embedding.
    """
    distances, indices = index.search(np.array([query_embedding]), top_k)
    return [chunks[i] for i in indices[0]]
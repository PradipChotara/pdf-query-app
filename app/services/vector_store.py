import faiss
import numpy as np
import pickle
import os
import logging

logger = logging.getLogger(__name__)

# Global flag to track vector store initialization status
_vector_store_initialized = False
_storage_base_dir = "data/storage" # Must match routes.py and be accessible in container

try:
    logger.info("Starting vector store initialization.")
    # Ensure the storage directory exists and is writable
    os.makedirs(_storage_base_dir, exist_ok=True)

    # Test write access to the storage directory
    test_file = os.path.join(_storage_base_dir, ".health_check_test_file")
    try:
        with open(test_file, "w") as f:
            f.write("health check test")
        os.remove(test_file)
        _vector_store_initialized = True # Set to True only upon successful initialization and write test
        logger.info("Vector store initialized and storage accessible.")
    except OSError as e:
        logger.error(f"Failed to write to vector store storage directory '{_storage_base_dir}': {e}")
        _vector_store_initialized = False
        raise # Re-raise to indicate a critical startup failure
except Exception as e:
    logger.error(f"Failed to initialize vector store or access storage: {e}")
    _vector_store_initialized = False
    raise # Re-raise to indicate a critical startup failure


def store_embeddings(embeddings: list[list[float]], chunks: list[str], pdf_id: str):
    """
    Stores embeddings in a FAISS index and saves the index and chunks to disk.
    """
    if not _vector_store_initialized:
        logger.error("Attempted to store embeddings before the vector store was initialized.")
        raise RuntimeError("Vector store not initialized.")

    # Create a FAISS index
    index = faiss.IndexFlatL2(len(embeddings[0]))
    index.add(np.array(embeddings))
    
    # Save the index and chunks
    index_path = os.path.join(_storage_base_dir, f"{pdf_id}.index")
    chunks_path = os.path.join(_storage_base_dir, f"{pdf_id}_chunks.pkl")

    try:
        faiss.write_index(index, index_path)
        with open(chunks_path, "wb") as f:
            pickle.dump(chunks, f)
        logger.info(f"Embeddings and chunks for {pdf_id} saved to disk.")
    except Exception as e:
        logger.error(f"Error saving embeddings for {pdf_id}: {e}")
        raise

def load_embeddings(pdf_id: str):
    """
    Loads the FAISS index and chunks for a given PDF.
    """
    if not _vector_store_initialized:
        logger.error("Attempted to load embeddings before the vector store was initialized.")
        raise RuntimeError("Vector store not initialized.")

    index_path = os.path.join(_storage_base_dir, f"{pdf_id}.index")
    chunks_path = os.path.join(_storage_base_dir, f"{pdf_id}_chunks.pkl")
    
    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        logger.warning(f"Index or chunks file not found for PDF ID '{pdf_id}'.")
        return None, None
    
    try:
        index = faiss.read_index(index_path)
        with open(chunks_path, "rb") as f:
            chunks = pickle.load(f)
        logger.info(f"Embeddings and chunks for {pdf_id} loaded from disk.")
        return index, chunks
    except Exception as e:
        logger.error(f"Error loading embeddings for {pdf_id}: {e}")
        raise

def search_similar_chunks(query_embedding: list[float], index: faiss.Index, chunks: list[str], top_k: int = 3):
    """
    Searches for the top_k most similar chunks to the query embedding.
    """
    if not _vector_store_initialized:
        logger.error("Attempted to search similar chunks before the vector store was initialized.")
        raise RuntimeError("Vector store not initialized.")
    if index is None or chunks is None:
        logger.warning("Attempted to search with uninitialized index or chunks.")
        return [] # Or raise an appropriate error

    distances, indices = index.search(np.array([query_embedding]), top_k)
    return [chunks[i] for i in indices[0]]

def is_vector_store_ready():
    """
    Returns True if the vector store is initialized and its storage is accessible, False otherwise.
    This function is used by the health check.
    """
    return _vector_store_initialized

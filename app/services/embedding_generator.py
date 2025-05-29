from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Global flag to track embedding model initialization status
_embedding_model_loaded = False
model = None # Initialize model as None

try:
    logger.info("Starting embedding model initialization.")
    # Load the pre-trained model
    # This can take significant time and memory as the model will be downloaded
    # if not already cached.
    model = SentenceTransformer('all-MiniLM-L6-v2')
    _embedding_model_loaded = True # Set to True only upon successful initialization
    logger.info("Embedding model initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize embedding model: {e}")
    _embedding_model_loaded = False # Ensure flag is False if initialization fails
    # Re-raising the exception to ensure the application doesn't proceed
    # in a broken state if the embedding generator is critical.
    raise

def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """
    Generates embeddings for a list of text chunks.
    """
    if not _embedding_model_loaded:
        logger.error("Attempted to generate embeddings before the model was loaded.")
        raise RuntimeError("Embedding model not initialized.")
    return model.encode(chunks).tolist()

def generate_embedding(text: str) -> list[float]:
    """
    Generates an embedding for a single text string (e.g., a query).
    """
    if not _embedding_model_loaded:
        logger.error("Attempted to generate a single embedding before the model was loaded.")
        raise RuntimeError("Embedding model not initialized.")
    return model.encode([text])[0].tolist()

def is_embedding_generator_ready():
    """
    Returns True if the embedding model has been successfully loaded, False otherwise.
    This function is used by the health check.
    """
    return _embedding_model_loaded

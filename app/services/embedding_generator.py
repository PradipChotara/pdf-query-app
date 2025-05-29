from sentence_transformers import SentenceTransformer

# Load the pre-trained model
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    """
    Generates embeddings for a list of text chunks.
    """
    return model.encode(chunks).tolist()

def generate_embedding(text: str) -> list[float]:
    """
    Generates an embedding for a single text string (e.g., a query).
    """
    return model.encode([text])[0].tolist()
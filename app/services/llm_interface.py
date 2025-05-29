from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global flag to track LLM initialization status
_llm_initialized = False

class LLMInterface:
    def __init__(self):
        global _llm_initialized
        logger.info("Starting LLM pipeline initialization.")
        try:
            # Initialize question-answering pipeline
            # This is where the model 'distilbert-base-uncased-distilled-squad' will be downloaded
            # if not already cached. This can take significant time and memory.
            self.qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
            _llm_initialized = True # Set to True only upon successful initialization
            logger.info("LLM pipeline initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize LLM pipeline: {e}")
            _llm_initialized = False # Ensure flag is False if initialization fails
            # Re-raising the exception to ensure the application doesn't proceed
            # in a broken state if the LLM is critical. Cloud Run will then restart the container.
            raise

    def get_llm_response(self, query: str, top_chunks: list) -> str:
        """
        Generate a response to the query using the top retrieved chunks as context.
        """

        # Ensure the LLM pipeline is initialized before attempting to use it
        if not _llm_initialized:
            logger.error("Attempted to use LLM pipeline before it was initialized.")
            return "Error: LLM pipeline not initialized. Please try again later."

        logger.info("-----inside get_llm_reponse() function-----")
        
        try:
            # Combine chunks into a single context and truncate
            context = "\n".join(top_chunks)
            if not context.strip():
                logger.warning("No relevant content found in the chunks.")
                return "No relevant content found in the PDF."
            context = context[:1000]  # Limit to ~1000 characters to avoid token overflow

            # Run question-answering pipeline
            logger.info(f"Running QA pipeline with query: {query}")
            result = self.qa_pipeline(question=query, context=context)
            answer = result["answer"]
            logger.info("-----after result-----")            

            # Format response to match existing structure
            response = (
                f"Based on the PDF content:\n{context}\n\n"
                f"Query: {query}\n\n"
                f"Response: {answer}"
            )
            logger.info(f"Generated LLM response for query: {query}")
            return response

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            # Ensure context is defined even if an error occurs before it's fully populated
            safe_context = context if 'context' in locals() else "N/A"
            return (
                f"Based on the PDF content:\n{safe_context}\n\n"
                f"Query: {query}\n\n"
                f"Response: Unable to generate answer due to an error."
            )

# Singleton instance - this will trigger the __init__ method when the module is imported
llm_interface = LLMInterface()

def is_llm_ready():
    """
    Returns True if the LLM pipeline has been successfully initialized, False otherwise.
    This function is used by the health check.
    """
    return _llm_initialized


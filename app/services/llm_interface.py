from transformers import pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMInterface:
    def __init__(self):
        # Initialize question-answering pipeline
        logger.info("Starting LLM pipeline initialization.")
        try:
            self.qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
            logger.info("LLM pipeline initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize LLM pipeline: {e}")
            raise

    def get_llm_response(self, query: str, top_chunks: list) -> str:
        """
        Generate a response to the query using the top retrieved chunks as context.
        """

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
            return (
                f"Based on the PDF content:\n{context}\n\n"
                f"Query: {query}\n\n"
                f"Response: Unable to generate answer due to an error."
            )

# Singleton instance
llm_interface = LLMInterface()
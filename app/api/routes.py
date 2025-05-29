from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Response # Added status and Response
from app.services import pdf_processor, embedding_generator, vector_store, llm_interface
import os
import logging
import sys

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

router = APIRouter()

# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the application is ready to serve.
    Checks the readiness of the LLM pipeline, embedding generator, and vector store.
    """
    health_status = {
        "llm_ready": False,
        "embedding_generator_ready": False,
        "vector_store_ready": False,
        "overall_status": "UNHEALTHY",
        "details": []
    }

    # Check LLM pipeline readiness
    if hasattr(llm_interface, 'is_llm_ready') and llm_interface.is_llm_ready():
        health_status["llm_ready"] = True
    else:
        health_status["details"].append("LLM pipeline is not ready.")
        logger.warning("Health check failed: LLM pipeline is not yet ready.")

    # Check Embedding Generator readiness
    if hasattr(embedding_generator, 'is_embedding_generator_ready') and embedding_generator.is_embedding_generator_ready():
        health_status["embedding_generator_ready"] = True
    else:
        health_status["details"].append("Embedding generator is not ready.")
        logger.warning("Health check failed: Embedding generator is not yet ready.")

    # Check Vector Store readiness (including storage access)
    if hasattr(vector_store, 'is_vector_store_ready') and vector_store.is_vector_store_ready():
        health_status["vector_store_ready"] = True
    else:
        health_status["details"].append("Vector store (or its underlying storage) is not ready.")
        logger.warning("Health check failed: Vector store is not yet ready.")

    # Determine overall status
    if (health_status["llm_ready"] and
        health_status["embedding_generator_ready"] and
        health_status["vector_store_ready"]):
        health_status["overall_status"] = "HEALTHY"
        logger.info("Health check successful: All critical components are ready.")
        return Response(status_code=status.HTTP_200_OK, content="OK")
    else:
        logger.error(f"Health check failed: {health_status['details']}")
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=f"UNHEALTHY: {', '.join(health_status['details'])}")


# Upload endpoint expecting form-data with a file
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Verify file is provided and is a PDF
    if not file:
        raise HTTPException(status_code=400, detail="No file provided.")
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF.")

    # Prepare storage directory
    storage_dir = "data/storage"
    os.makedirs(storage_dir, exist_ok=True)
    file_path = os.path.join(storage_dir, file.filename)

    # Save the uploaded file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()  # Async read of file content
            if not content:
                raise ValueError("File is empty.")
            f.write(content)
        logger.info(f"File saved successfully: {file_path}")
    except Exception as e:
        logger.error(f"Error saving file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save the uploaded file.")

    # Process the PDF
    try:
        text = pdf_processor.extract_text_from_pdf(file_path)
        if not text.strip():
            raise ValueError("No text extracted from PDF.")
        chunks = pdf_processor.split_text_into_chunks(text)
        embeddings = embedding_generator.generate_embeddings(chunks)
        vector_store.store_embeddings(embeddings, chunks, file.filename)
        logger.info(f"PDF {file.filename} processed and embeddings stored.")
    except Exception as e:
        logger.error(f"Error processing PDF {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the PDF.")

    return {"pdf_id": file.filename}

# Query endpoint expecting form-data with fields
@router.post("/query")
async def query_pdf(
    pdf_id: str = Form(...),
    query: str = Form(...)
):
    # Validate form parameters
    if not pdf_id.strip():
        raise HTTPException(status_code=400, detail="pdf_id cannot be empty.")
    if not query.strip():
        raise HTTPException(status_code=400, detail="query cannot be empty.")

    logger.info(f"-----Received query - pdf_id: {pdf_id}, query: {query}-----")

    # Load embeddings and chunks
    try:
        index, chunks = vector_store.load_embeddings(pdf_id)
        if not index:
            logger.warning(f"PDF with ID '{pdf_id}' not found.")
            raise HTTPException(status_code=404, detail=f"PDF with ID '{pdf_id}' not found.")
        else:
            logger.info(f"-----Embeddings loaded -'{pdf_id}'.-----")
        if chunks is not None:
            logger.info(f"-----Document chunks loaded - '{pdf_id}'. No of chunks: {len(chunks)}-----")
        else:
            logger.warning(f"No document chunks found for PDF ID '{pdf_id}'.")
    except Exception as e:
        logger.error(f"Error loading embeddings for {pdf_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load PDF data.")

    # Generate query response
    try:
        query_embedding = embedding_generator.generate_embedding(query)
        top_chunks = vector_store.search_similar_chunks(query_embedding, index, chunks, top_k=3)
        llm_response = llm_interface.llm_interface.get_llm_response(query, top_chunks)
        logger.info(f"Response generated for query on {pdf_id}")
        return {"response": llm_response}  # Return the actual response
    except Exception as e:
        logger.error(f"Error generating response for {pdf_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response.")

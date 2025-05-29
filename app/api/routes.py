from fastapi import APIRouter, UploadFile, File, Form, HTTPException
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

@router.get("/")
async def root():
    log_message = "Server is running and the root endpoint was accessed."
    logger.info(log_message)
    return {"response": "SERVER IS RUNNNNIIIINGGGGGG"}

@router.get("/test")
async def test():
    log_message = "inside test API"
    logger.info(log_message)
    return {"response": "test is working"}

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
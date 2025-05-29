# PDF Query

## Setup

Run the following command to create a virtual environment named `venv`:
```bash
python -m venv pdf_query_env
```

Install dependencies:
```bash
pip install -r requirements.txt
```
Run the app:
```bash
uvicorn app.main:app --reload
```

## Usage

Upload a PDF: Send a POST request to /upload with a PDF file.<br>
Query the PDF: Send a POST request to /query with pdf_id and query parameters.

## Example:

Upload:
```bash
curl -X POST -F "file=@path/to/your/file.pdf" http://localhost:8000/upload
```
Query:
```bash
curl -X POST -d "pdf_id=yourfile.pdf&query=your query here" http://localhost:8000/query
```

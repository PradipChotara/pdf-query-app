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

## TEST

```bash
Invoke-WebRequest -Uri 'http://<your_vm_ip>:7000/health' -Method Get
```

```bash
$filePath = 'C:\Users\pradip\Downloads\test.pdf' # Adjust the path if running on the VM

$boundary = [System.Guid]::NewGuid().ToString()
$contentType = "multipart/form-data; boundary=$boundary"

$body = "--$boundary`r`n"
$body += "Content-Disposition: form-data; name=`"file`"; filename=`"$((Split-Path $filePath -Leaf))`"`r`n"
$body += "Content-Type: application/pdf`r`n`r`n"
$body += ([System.IO.File]::ReadAllBytes($filePath) | Out-String) + "`r`n"
$body += "--$boundary--`r`n"

Invoke-WebRequest -Uri 'http://<your_vm_ip>:7000/upload' -Method Post -ContentType $contentType -Body $body
```

```bash
Invoke-WebRequest -Uri 'http://<your_vm_ip>:7000/query' -Method Post -Body @{
    pdf_id = 'test.pdf';
    query  = 'which dataset is being used here'
}
```

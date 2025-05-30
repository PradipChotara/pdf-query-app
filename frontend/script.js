document.addEventListener('DOMContentLoaded', () => {
    // Get references to elements
    const queryForm = document.getElementById('queryForm'); // This form now handles both upload and query
    const pdfFile = document.getElementById('pdfFile');
    const queryText = document.getElementById('queryText');
    const submitBtn = document.getElementById('submitBtn'); // The single button for both actions
    const buttonText = document.getElementById('buttonText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const responseArea = document.getElementById('responseArea');
    const responseText = document.getElementById('responseText');
    const messageArea = document.getElementById('messageArea');

    // Base URL for your FastAPI backend
    const API_BASE_URL = 'http://localhost:8000'; // Change this to your deployed Cloud Run URL later

    // Function to display messages to the user
    function displayMessage(message, type) {
        messageArea.innerHTML = `<div class="alert alert-${type}" role="alert">${message}</div>`;
        // Clear message after a few seconds
        setTimeout(() => {
            messageArea.innerHTML = '';
        }, 5000);
    }

    // Function to set loading state for the single "Upload & Query" button
    function setLoading(isLoading) {
        submitBtn.disabled = isLoading;
        if (isLoading) {
            buttonText.textContent = 'Processing...';
            loadingSpinner.classList.remove('d-none');
            responseArea.classList.add('d-none'); // Hide previous response
            responseText.textContent = '';
        } else {
            buttonText.textContent = 'Upload & Query';
            loadingSpinner.classList.add('d-none');
        }
    }

    // Function to perform the health check
    function performHealthCheck() {
        fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
        })
        .then(response => {
            if (response.ok) {
                return response.text();
            } else {
                return response.text().then(text => Promise.reject({ status: response.status, statusText: response.statusText, text }));
            }
        })
        .then(healthResult => {
            console.log("Health check successful:", healthResult);
            displayMessage("Backend is healthy!", 'success');
        })
        .catch(error => {
            console.error("Health check failed:", error);
            let errorMessage = `Backend health check failed: `;
            if (error.status) {
                errorMessage += `${error.status} ${error.statusText}. Details: ${error.text}`;
            } else {
                errorMessage += `${error.message}. Is the server running?`;
            }
            displayMessage(errorMessage, 'danger');
        });
    }

    // Event listener for the form submission (now handles both upload and query)
    queryForm.addEventListener('submit', function(event) { // Removed 'async'
        event.preventDefault(); // Prevent default form submission

        setLoading(true); // Set loading for the single button
        messageArea.innerHTML = ''; // Clear previous messages

        const file = pdfFile.files[0];
        console.log('Selected file:', file);
        const query = queryText.value.trim();

        if (!file) {
            displayMessage('Please select a PDF file to upload.', 'danger');
            setLoading(false);
            return;
        }

        if (!query) {
            displayMessage('Please enter a query.', 'danger');
            setLoading(false);
            return;
        }

        if (file.type !== 'application/pdf') {
            displayMessage('Invalid file type. Please upload a PDF.', 'danger');
            setLoading(false);
            return;
        }

        // --- Step 1: Upload the PDF ---
        displayMessage('Uploading PDF...', 'info');
        const uploadFormData = new FormData();
        uploadFormData.append('file', file);

        displayMessage('test.....1', 'info');

        setTimeout(function() {
            console.log('Delayed execution after 2 seconds');
        }, 5000); // Delay of 2000 milliseconds (2 seconds)

        let pdfId = null;
        fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: uploadFormData,
        })
        .then(uploadResponse => {
            displayMessage('test.....2', 'info');
            if (uploadResponse.ok) {
                displayMessage('test.....3', 'info');
                return uploadResponse.json();
            } else {
                displayMessage('test.....4', 'info');
                return uploadResponse.json().then(errorData => {
                    console.error('Upload error response:', errorData);
                    return Promise.reject({ status: uploadResponse.status, statusText: uploadResponse.statusText, detail: errorData.detail || 'Failed to upload PDF.' });
                });
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            throw error; // Rethrow to ensure the outer .catch handles it
        })
        .then(uploadResult => {
            displayMessage('test.....5', 'info');
            pdfId = uploadResult.pdf_id;
            displayMessage(`PDF uploaded successfully. PDF ID: ${pdfId}`, 'success');
            console.log(`PDF uploaded successfully. PDF ID: ${pdfId}`);

            // --- Step 2: Query the PDF ---
            displayMessage('Processing query...', 'info');
            const queryFormData = new FormData();
            queryFormData.append('pdf_id', pdfId); // Use the pdfId obtained from the upload response
            queryFormData.append('query', query);

            return fetch(`${API_BASE_URL}/query`, {
                method: 'POST',
                body: queryFormData,
            });
        })
        .then(queryResponse => {
            if (queryResponse.ok) {
                return queryResponse.json();
            } else {
                return queryResponse.json().then(errorData => Promise.reject({ status: queryResponse.status, statusText: queryResponse.statusText, detail: errorData.detail || 'Failed to get query response.' }));
            }
        })
        .then(queryResult => {
            responseText.textContent = queryResult.response;
            responseArea.classList.remove('d-none'); // Show response area
            displayMessage('Query successful! See response below.', 'success');
            console.log('Query successful!');
        })
        .catch(error => {
            console.error("Error:", error);
            let errorMessage = "An error occurred: ";
            if (error.detail) {
                errorMessage += error.detail;
            } else if (error.status) {
                errorMessage += `${error.status} ${error.statusText}`;
            } else {
                errorMessage += error.message || error;
            }
            displayMessage(errorMessage, 'danger');
        })
        .finally(() => {
            setLoading(false); // Always reset loading state
            // performHealthCheck(); // Perform health check after query (or upload failure)
            displayMessage('test.....in_finally', 'info');
        });
    });

    // Perform an initial health check when the page loads
    performHealthCheck();
});
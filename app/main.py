from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Import CORSMiddleware
from app.api import routes

app = FastAPI()

# --- CORS Configuration ---
# Define the origins that are allowed to make requests to your FastAPI application.
# For local development, include localhost and common development ports.
# For deployed applications, replace "YOUR_DEPLOYED_FRONTEND_URL_HERE" with the actual URL
# where your frontend is hosted (e.g., from Cloud Storage, Firebase Hosting, etc.).
origins = [
    "http://localhost",          # Allow requests from localhost (development)
    "http://localhost:8000",     # If your frontend is served from the same port as backend during local dev
    "http://localhost:8080",
    "http://127.0.0.1:5500",     # Common alternative local port for frontend
    "null",                      # For file:// access (when opening index.html directly from file system)
    # IMPORTANT: When deploying your frontend, add its actual URL here.
    # Example: "https://your-frontend-app.web.app",
    # Example: "https://your-cloud-run-frontend-service-url.run.app"
    # Be cautious with "*" in production; it allows all origins and is a security risk.
    # If your frontend is deployed to Cloud Run, it will have a URL like https://<service-name>-<hash>-<region>.run.app
    # Add that specific URL here.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,     # Allow cookies to be sent with cross-origin requests (if your app uses them)
    allow_methods=["*"],        # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],        # Allow all headers in the request
)
# --- End CORS Configuration ---

# Include API routes from your routes.py file
app.include_router(routes.router)

# Optional: This block is typically used for local development when running main.py directly
# If you run your app via 'uvicorn main:app --reload', this block is not strictly necessary
# # but it's good practice for standalone execution.
# if __name__ == "__main__":
#     import uvicorn
#     # The --reload flag should only be used for local development, not in production.
#     uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.ask import process_query

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class QueryRequest(BaseModel):
    query: str
    session_id: str  # Add session ID to track conversation

@app.get("/")
async def root():
    return {"message": "Test"}

@app.post("/ask")
def ask_endpoint(request: QueryRequest):
    try:
        response = process_query(request.query, request.session_id)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
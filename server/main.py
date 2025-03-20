from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.ask import process_query

app = FastAPI()
allowed_origins = [
    "https://cs-chatbot-gze2kq6oq-moisesxtians-projects.vercel.app"  # Your React frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Change "*" to frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Allow only necessary methods
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
# utils/ask.py

import os
import chromadb
from dotenv import load_dotenv
from groq import Groq
from collections import defaultdict

# Load environment variables
load_dotenv()

# Setup ChromaDB client
CHROMA_PATH = r"chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="growing_vegetables")

# Setup Groq API
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")
client = Groq(api_key=api_key)

# Session-based memory
chat_memory = defaultdict(list)

def get_contextual_query(user_query: str, session_id: str, n_history: int = 2) -> str:
    """Combine the latest user query with past user messages to enhance context."""
    history = chat_memory[session_id]
    recent_user_msgs = [msg["content"] for msg in history if msg["role"] == "user"][-n_history:]
    
    # Combine recent history + current question
    if recent_user_msgs:
        context_query = " ".join(recent_user_msgs) + " " + user_query
    else:
        context_query = user_query

    print(f"Contextual Query: {context_query}")
    return context_query


def process_query(user_query: str, session_id: str) -> str:
    print(f"Received query: {user_query}")
    print(f"Session ID: {session_id}")

    # STEP 1: Get contextual query
    context_query = get_contextual_query(user_query, session_id)

    # STEP 2: Query ChromaDB
    results = collection.query(
        query_texts=[context_query],
        n_results=1
    )
    print("ChromaDB query results:", results)

    documents = results.get('documents', [])
    if not documents:
        return "I don't know"

    # STEP 3: System Prompt
    system_prompt = f"""
    You are a sales representative for a company. Your name is Armando S. Moises. You prioritize customer satisfaction and you respond with
    a friendly and helpful tone.
    You are an expert in sales and marketing. DO NOT ANSWER IF YOU ARE UNSURE,
    YOU MAY ASK FOR SPECIFICATIONS OF WHAT THE USER NEEDS BEFORE ANSWERING. 
    if you are not sure which category the user is asking, Ask for Clarification.
    Be Specific, and try to upsell the customer
    ------------------------------
    Example of how you talk: Hi Mark!☺️ just following up, would you like me to proceed with the diagnostic for your aircon?❄️ 
    because our technician can check and fix minor issues on the spot! Let me know, and I'll arrange it for you!🧑‍🔧
    Only answer based on the provided knowledge.
    If you don't know the answer, just say: I don't know
    ------------------------------
    The data:
    {documents}
    """

    # STEP 4: Update session memory
    chat_memory[session_id].append({"role": "user", "content": user_query})

    # STEP 5: LLM call
    messages = [{"role": "system", "content": system_prompt}] + chat_memory[session_id]

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            stream=False,
        )
        assistant_reply = chat_completion.choices[0].message.content
    except Exception as e:
        print(f"LLM Error: {e}")
        assistant_reply = "⚠️ There was an issue generating a response."

    # STEP 6: Save assistant response to memory
    chat_memory[session_id].append({"role": "assistant", "content": assistant_reply})

    return assistant_reply


# Optional: reset chat memory per session
def reset_memory(session_id: str):
    if session_id in chat_memory:
        chat_memory[session_id] = []

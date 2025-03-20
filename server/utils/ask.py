import os
import chromadb
from dotenv import load_dotenv
from groq import Groq
from collections import defaultdict

# Load environment variables
load_dotenv()

# Setup ChromaDB client (ensure you use the same collection name as in your fill_db.py)
CHROMA_PATH = r"chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="services")

# Setup Groq API
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")
client = Groq(api_key=api_key)

# Session-based memory and intent tracking
chat_memory = defaultdict(list)
session_intents = {}

def detect_intent(query: str) -> str:
    """
    Naively detect the intent (main service category) from the query.
    Customize this function as needed.
    """
    query_lower = query.lower()
    if "aircon" in query_lower or "ac" in query_lower:
        return "Aircon"
    elif "clean" in query_lower and "home" in query_lower:
        return "Home_Cleaning"
    elif "deep clean" in query_lower:
        return "Deep_Cleaning"
    elif "carpet" in query_lower or "upholstery" in query_lower:
        return "Carpet_&_Upholstery"
    elif "manicure" in query_lower or "pedicure" in query_lower or "nail" or "eyelashes" or "lashes"in query_lower:
        return "Home_Beauty"
    elif "massage" in query_lower:
        return "Massage"
    elif "handyman" in query_lower:
        return "Handyman"
    elif "pet" in query_lower:
        return "Pet_Care"
    elif "elder" in query_lower:
        return "Elder_Care"
    else:
        return "General"

def get_contextual_query(user_query: str, session_id: str, n_history: int = 2) -> str:
    """
    Combine the latest user query with past user messages to enhance context.
    Reset the conversation history if the detected intent (main category) changes.
    """
    current_intent = detect_intent(user_query)
    previous_intent = session_intents.get(session_id)
    if previous_intent and previous_intent != current_intent:
        chat_memory[session_id] = []
        print(f"Intent changed from '{previous_intent}' to '{current_intent}'. Resetting context.")
    session_intents[session_id] = current_intent

    # Get recent user messages for context
    history = chat_memory[session_id]
    recent_user_msgs = [msg["content"] for msg in history if msg["role"] == "user"][-n_history:]
    
    # Combine recent history with current query
    context_query = " ".join(recent_user_msgs + [user_query]) if recent_user_msgs else user_query

    # If query includes pricing-related keywords, append "pricing" to the query
    query_lower = user_query.lower()
    if any(keyword in query_lower for keyword in ["price", "cost", "how much", "pricing","rate", "fee"]):
        context_query += " pricing rate"

    
    print(f"Contextual Query: {context_query}")
    return context_query

def process_query(user_query: str, session_id: str) -> str:
    print(f"Received query: {user_query}")
    print(f"Session ID: {session_id}")

    # STEP 1: Get contextual query with intent handling
    context_query = get_contextual_query(user_query, session_id)

    # STEP 2: Query ChromaDB (optionally adjust n_results or add a 'where' clause if supported)
    results = collection.query(
        query_texts=[context_query],
        n_results=1 # Adjust as needed
    )
    print("ChromaDB query results:", results)

    documents = results.get('documents', [])
    # Check that we have non-empty results; results are nested in a list
    if not documents or not documents[0]:
        return "I don't know"

    # STEP 3: Prepare the system prompt for the LLM
    system_prompt = f"""
You are a sales representative for a company. Your name is Armando S. Moises. You prioritize customer satisfaction and respond in a friendly and helpful tone.
You are an expert in sales and marketing. DO NOT ANSWER IF YOU ARE UNSURE; you may ask for specifications of what the user needs before answering.
If you are not sure which category the user is asking about, ask for clarification.
Be specific, and try to upsell the customer.
------------------------------
Example: Hi Mark!☺️ Just following up – would you like me to proceed with the diagnostic for your aircon?❄️ 
Our technician can check and fix minor issues on the spot! Let me know, and I'll arrange it for you!🧑‍🔧
Only answer based on the provided knowledge. Do not make up answers.

You are chatting in a message format, Format your messages in a more readable format. 
------------------------------
IMPORTANT: DO NOT MAKE UP A REPLY especially if you don't have the information. if information is not in the data, say that you currently offer that service or its not available
The data:
{documents}
"""

    # STEP 4: Update session memory with the user query
    chat_memory[session_id].append({"role": "user", "content": user_query})

    # STEP 5: Combine system prompt and conversation history for the LLM call
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

    # STEP 6: Save the assistant's reply to session memory
    chat_memory[session_id].append({"role": "assistant", "content": assistant_reply})

    return assistant_reply

def reset_memory(session_id: str):
    """Reset the chat memory and intent for a given session."""
    if session_id in chat_memory:
        chat_memory[session_id] = []
    if session_id in session_intents:
        del session_intents[session_id]

import os
import docx
import chromadb
from chromadb.config import Settings
from tqdm import tqdm

DATA_DIR = r"data"  # adjust path if needed
CHROMA_PATH = r"chroma_db"

# ChromaDB setup
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="services")

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text.strip() for para in doc.paragraphs if para.text.strip()])

def process_folder(folder_path):
    docs = []
    metadatas = []
    ids = []
    counter = 0

    for root, _, files in os.walk(folder_path):
        for file in tqdm(files):
            if file.endswith(".docx"):
                full_path = os.path.join(root, file)
                text = extract_text_from_docx(full_path)
                if text:
                    docs.append(text)
                    metadatas.append({"source": full_path})
                    ids.append(f"doc_{counter}")
                    counter += 1
    return docs, metadatas, ids

if __name__ == "__main__":
    documents, metadatas, ids = process_folder(DATA_DIR)
    
    print(f"Inserting {len(documents)} documents into ChromaDB...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("✅ Done populating ChromaDB!")

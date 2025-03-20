from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import os

# setting the environment
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="growing_vegetables")

# loading the documents
loader = PyPDFDirectoryLoader(DATA_PATH)
raw_documents = loader.load()

# splitting the documents
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

chunks = text_splitter.split_documents(raw_documents)

# preparing data to be added into chromadb
documents = []
metadata = []
ids = []

i = 0

for chunk in chunks:
    # Extract file name for service tag
    source_path = chunk.metadata.get('source', '')
    file_name = os.path.basename(source_path).replace('.pdf', '').strip()

    documents.append(chunk.page_content)
    ids.append("ID" + str(i))
    metadata.append({
        **chunk.metadata,
        "service": file_name  # <-- add service name from filename!
    })

    i += 1

# upserting to chromadb
collection.upsert(
    documents=documents,
    metadatas=metadata,
    ids=ids
)
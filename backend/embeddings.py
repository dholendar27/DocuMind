import os
from llama_index.core import SimpleDirectoryReader
from llama_index.embeddings.google import GeminiEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SimpleNodeParser
import chromadb
from dotenv import load_dotenv

load_dotenv()

EXTRACTED_FILEPATH = "extracted"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("rag_kb")

def document_loader(file_path):
    # Load raw documents
    reader = SimpleDirectoryReader(input_files=[file_path])
    document = reader.load_data()

    return document 

def document_embeddings(filepath):
    embed_model = GeminiEmbedding(
        model_name="models/gemini-embedding-001",
        api_key=GEMINI_API_KEY
    )

    # Use extracted markdown file if it exists, otherwise use original file
    if filepath.endswith('.md') or os.path.exists(filepath):
        document = document_loader(filepath)
    else:
        print(f"Warning: File not found at {filepath}")
        return None

    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    return VectorStoreIndex.from_documents(
        documents=document,
        storage_context=storage_context,
        embed_model=embed_model
    )

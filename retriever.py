import os
from llama_index.embeddings.google import GeminiEmbedding
from llama_index.core import PromptTemplate
from llama_index.core import VectorStoreIndex
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

prompt = PromptTemplate(
    """
        <task>
            <role>
                You are a reliable assistant that answers user queries by grounding your responses in retrieved documents.
            </role>
            <objective>
                Ensure the answer is accurate, concise, and based strictly on the provided context.
            </objective>
            <context>
                {context_str}
            </context>
            <instruction>
                Use only the information inside the <context> section to answer.
            </instruction>
            <instruction>
                If the context is incomplete, state this clearly and avoid guessing.
            </instruction>
            <instruction>
                When multiple sources are relevant, synthesize them into a single coherent response.
            </instruction>
            <instruction>
                Do not include unrelated or fabricated details.
            </instruction>
            <query>
                {query_str}
            </query>
            <answer>
                Provide a clear, helpful, and well-structured response.
            </answer>
        </task>
    """
)

llm = GoogleGenAI(
    model="gemini-2.0-flash-lite",
    api_key=GEMINI_API_KEY
)

db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection("rag_kb")

embed_model = GeminiEmbedding(
        model_name="models/gemini-embedding-001",
        api_key=GEMINI_API_KEY
    )

vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=embed_model
)


query_engine = index.as_query_engine(text_qa_template=prompt, llm=llm)

def response(query):
    response = query_engine.query(query)
    print("response:",response)
    return response
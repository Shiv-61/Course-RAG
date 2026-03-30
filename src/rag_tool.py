import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from crewai.tools import BaseTool
from pydantic import Field
from typing import Type

EMBEDDINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "embeddings")

class CatalogRetrievalToolInput(BaseTool):
    pass

class CatalogRetrievalTool(BaseTool):
    name: str = "Catalog Retrieval Tool"
    description: str = (
        "Search the university catalog for program requirements, course descriptions, "
        "prerequisites, and academic policies. Use this tool to answer any questions "
        "about courses, credits, and prerequisites. Always include the source citation from the results."
    )
    
    def _run(self, query: str) -> str:
        """Search the FAISS vector database."""
        if not os.path.exists(EMBEDDINGS_DIR) or not os.listdir(EMBEDDINGS_DIR):
            return "Error: Vector database not found. Please run the ingestion script first."
            
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # Allow dangerous deserialization because we generated this index locally
        vector_store = FAISS.load_local(EMBEDDINGS_DIR, embeddings, allow_dangerous_deserialization=True)
        
        # Retrieve top 3 most similar chunks to save tokens
        docs = vector_store.similarity_search(query, k=3)
        
        if not docs:
            return "I don't have that information in the provided catalog/policies."
            
        results = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown source')
            results.append(f"--- Result {i+1} ---\nSource: {source}\nContent: {doc.page_content}\n")
            
        return "\n".join(results)

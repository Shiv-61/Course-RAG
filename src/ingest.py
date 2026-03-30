import os
from langchain_community.document_loaders import PyPDFLoader, BSHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
EMBEDDINGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "embeddings")

def ingest_data():
    documents = []
    
    # Check if data directory exists
    if not os.path.exists(DATA_DIR):
        print(f"Data directory {DATA_DIR} not found.")
        return
    print("Loading documents from:", DATA_DIR)
    
    # Load all PDFs and HTMLs
    for file in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, file)
        
        try:
            if file.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                for doc in docs:
                    doc.metadata['source'] = file
                    # To track pages for citations
                    if 'page' in doc.metadata:
                        doc.metadata['source'] = f"{file} (Page {doc.metadata['page']})"
                documents.extend(docs)
                print(f"Loaded PDF: {file}")
            elif file.endswith('.html') or file.endswith('.htm'):
                loader = BSHTMLLoader(file_path)
                docs = loader.load()
                for doc in docs:
                    doc.metadata['source'] = file
                documents.extend(docs)
                print(f"Loaded HTML: {file}")
        except Exception as e:
            print(f"Error loading {file}: {e}")

    print(f"Total pages/documents loaded: {len(documents)}")

    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Total chunks created: {len(chunks)}")
    
    print("Initializing embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Building FAISS vector store...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
    vector_store.save_local(EMBEDDINGS_DIR)
    print(f"Vector store successfully saved to {EMBEDDINGS_DIR}")

if __name__ == "__main__":
    ingest_data()

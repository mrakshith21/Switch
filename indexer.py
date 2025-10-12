from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
import os
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import FAISS

INDEX_PATH = "./faiss_index"
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_language(file_name: str) -> Language:
    extension = file_name.split(".")[-1].lower()
    if extension in ["py"]:
        return Language.PYTHON

def create_index():
    for root, dirs, files in os.walk("."):
        path = root.split(os.sep)
        for file_name in files:
            print("Indexing file path:",file_name)

            # Get language
            language = get_language(file_name)
            if language:
                file_path = os.path.join(root, file_name)

                # Read file
                with open(file_path, "r", encoding="utf-8") as f:
                    code_str = f.read()

                # Create documents using langchain splitters
                splitter = RecursiveCharacterTextSplitter.from_language(
                    language=language,
                    chunk_size=50,
                    chunk_overlap=0,
                )
                docs = splitter.create_documents([code_str])
                
                # Add metadata to chunks, including source file path
                for doc in docs:
                    doc.metadata["source_path"] = file_path

                # Create embeddings
                faiss_index = FAISS.from_documents(docs, embedding_model)

                # Store embeddings
                faiss_index.save_local(INDEX_PATH)


def query_index(prompt: str):

    print(embedding_model)
    # Load existing index
    faiss_index = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)

    # Perform similarity search
    print("Querying for prompt:", prompt)
    results = faiss_index.similarity_search(prompt, k=5)

    # Print results with source file paths
    for i, result in enumerate(results):
        print(f"Result {i+1}:")
        print(f"Source Path: {result.metadata.get('source_path', 'N/A')}")
        print(f"Content: {result.page_content}")
        print("-" * 40)
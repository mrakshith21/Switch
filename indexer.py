from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
import os
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import time
import re

INDEX_PATH = "./faiss_index"
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


IGNORE_PATH = [
    'node_modules',
    ".venv",
    "__pycache__",
    ".git",
]


def get_language(file_name: str) -> Language:
    extension = file_name.split(".")[-1].lower()
    if extension in ["py"]:
        return Language.PYTHON
    elif extension in ["java"]:
        return Language.JAVA
    elif extension in ["js", "jsx", "ts", "tsx"]:
        return Language.JS

def should_index(file_path: str) -> bool:

    for pattern in IGNORE_PATH:
        if pattern in file_path:
            return False
    return True

def create_index():
    start_time = time.time()
    vector_store = None
    for root, dirs, files in os.walk("."):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            if not should_index(file_path):
                print("Skipping file path:",file_path)
                continue
            print("Indexing file path:",file_path)

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
                    chunk_size=200,
                    chunk_overlap=50,
                )
                docs = splitter.create_documents([code_str])
                
                    
                # Add metadata to chunks, including source file path
                for doc in docs:
                    doc.metadata["source_path"] = file_path
                docs = add_loc_lines_to_docs(docs, code_str)

                
                if vector_store is None:
                    vector_store = FAISS.from_documents(docs, embedding_model)
                else:
                    vector_store.add_documents(docs)

    end_time = time.time()
    
    if vector_store:
        vector_store.save_local(INDEX_PATH)
    else:
        print("No documents were indexed; index not created.")
    print(f"Indexing completed in {end_time - start_time:.2f} seconds.")

def query_index(prompt: str) -> list[Document]:

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
        print(f'Metadata: {result.metadata}')
        print("-" * 40)
    
    return results

def add_loc_lines_to_docs(docs, original_text):
    """
    Mutates docs in place: adds metadata['loc'] = {'lines': {'from': start_line, 'to': end_line}}
    Assumes docs are in the same order as the chunks in original_text.
    """
    # Normalize newlines so counts match (optional but recommended)
    # If your original_text may contain CRLF, normalize to '\n' first and ensure docs were produced from same text.
    text = original_text.replace("\r\n", "\n")
    current_pos = 0

    for d in docs:
        chunk = d.page_content
        # Normalize chunk the same way
        chunk_norm = chunk.replace("\r\n", "\n")

        # Try exact find starting from current_pos to handle duplicates
        start_char = text.find(chunk_norm, current_pos)
        if start_char == -1:
            # Try trimming leading/trailing whitespace as splitter may trim separators
            trimmed = chunk_norm.strip()
            if trimmed:
                start_char = text.find(trimmed, current_pos)
        if start_char == -1:
            # Worst case: search from beginning
            start_char = text.find(chunk_norm)
        if start_char == -1:
            # Give up: set to current_pos (best-effort fallback)
            start_char = current_pos

        end_char_exclusive = start_char + len(chunk_norm)

        # Convert char offsets to 1-indexed line numbers
        start_line = text.count("\n", 0, start_char) + 1
        # use end_char_exclusive - 1 to count the line of last character of chunk
        end_line = text.count("\n", 0, max(0, end_char_exclusive - 1)) + 1

        # Attach to metadata, preserving any existing metadata
        if not hasattr(d, "metadata") or d.metadata is None:
            d.metadata = {}
        d.metadata["loc"] = {"lines": {"from": start_line, "to": end_line}}

        # Advance pointer so subsequent identical chunks match the next occurrence
        current_pos = end_char_exclusive

    return docs
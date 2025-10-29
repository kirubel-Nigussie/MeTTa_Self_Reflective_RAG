import os
import gc
import PyPDF2
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings
from utils.text_utils import clean_text

os.makedirs("./data/uploads", exist_ok=True)

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len
        )

    def process_file(self, file_path: str) -> List[Document]:
        """
        Loads the document, splits it into chunks, and returns LangChain Document objects.
        """
        text = ""
        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    page_text = page.extract_text() or ""
                    text += clean_text(page_text) + "\n\n"
        except Exception as e:
            print(f"Error reading PDF file {file_path}: {e}")
            return []

        # Split into chunks using LangChain's proven splitter
        chunks = self.text_splitter.split_text(text)
        
        # Convert to Document objects with metadata
        base_name = os.path.basename(file_path)
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append(
                Document(
                    page_content=chunk, 
                    metadata={
                        "source": base_name,
                        "chunk_id": f"{base_name}_chunk_{i+1}",
                        "chunk_index": i + 1
                    }
                )
            )
        
        print(f"📄 Processed {base_name}: {len(documents)} chunks created")
        return documents

# Global instance
document_processor = DocumentProcessor()

def save_pdf(file_storage):
    """Save uploaded PDF file to disk."""
    filename = file_storage.filename
    path = os.path.join("./data/uploads", filename)
    file_storage.save(path)
    return path

def pdf_to_chunks(path):
    """
    Convert PDF to chunks using LangChain's proven approach.
    Returns list of chunk dictionaries compatible with existing code.
    """
    documents = document_processor.process_file(path)
    
    # Convert LangChain Documents to the format expected by existing code
    chunks = []
    for doc in documents:
        chunks.append({
            "id": doc.metadata["chunk_id"],
            "text": doc.page_content,
            "metadata": doc.metadata
        })
    
    return chunks

def stream_pdf_chunks(path):
    """
    Generator that yields chunks from PDF using LangChain processing.
    Maintains compatibility with existing streaming approach.
    """
    chunks = pdf_to_chunks(path)
    for chunk in chunks:
        yield chunk